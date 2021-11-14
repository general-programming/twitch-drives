# Code from https://github.com/tdorssers/TeslaPy but more async

import ast
import asyncio
import pkgutil
import json
import os
import json
from typing import List
import time
import logging
import aiohttp
import urllib
from httpx import USE_CLIENT_DEFAULT
from authlib.integrations.httpx_client import AsyncOAuth2Client
from twitchdrives.common import get_redis
from twitchdrives.exceptions import VehicleError, VehicleAsleep, VehicleTimeout

logger = logging.getLogger(__name__)
SSO_BASE_URL = "https://auth.tesla.com/"
SSO_CLIENT_ID = "ownerapi"
API_BASE_URL = "https://owner-api.teslamotors.com/"
STREAMING_BASE_URL = 'wss://streaming.vn.teslamotors.com/'


async def get_tesla():
    return await AsyncTesla.create(
        scope=("openid", "email", "offline_access"),
        redirect_uri=SSO_BASE_URL + 'void/callback',
        token_endpoint=SSO_BASE_URL + 'oauth2/v3/token',
        headers={
            "Content-Type": "application/json",
            'User-Agent': "Tesla/1.0.0"
        },
    )


class Vehicle(dict):
    COLS = ['speed', 'odometer', 'soc', 'elevation', 'est_heading', 'est_lat',
            'est_lng', 'power', 'shift_state', 'range', 'est_range', 'heading']

    def __init__(self, vehicle, tesla):
        super(Vehicle, self).__init__(vehicle)
        self.tesla = tesla
        self.callback = None

    async def get_vehicle_data(self):
        """ A rollup of all the data request endpoints plus vehicle config """
        data = await self.api('VEHICLE_DATA')
        if data["response"]:
            self.update(data['response'])
        return self

    async def get_vehicle_summary(self):
        """ Determine the state of the vehicle's various sub-systems """
        summary = await self.api('VEHICLE_SUMMARY')
        if summary["response"]:
            self.update(summary['response'])
        return self

    async def wake_up(self, timeout=60, interval=2, backoff=1.15):
        logger.info('%s is %s', self['display_name'], self['state'])
        await self.get_vehicle_summary()

        if self['state'] != 'online':
            await self.api('WAKE_UP')  # Send wake up command
            start_time = time.time()
            while self['state'] != 'online':
                logger.debug('Waiting for %d seconds', interval)
                await asyncio.sleep(int(interval))
                # Get vehicle status
                await self.get_vehicle_summary()
                # Raise exception when task has timed out
                if start_time + timeout < time.time():
                    raise VehicleError('%s not woken up within %s seconds'
                                       % (self['display_name'], timeout))
                interval *= backoff
            logger.info('%s is %s', self['display_name'], self['state'])

    async def _parse_msg(self, socket, message):
        """ Parse messages """
        msg = json.loads(message.data)
        if msg['msg_type'] == 'control:hello':
            logger.debug('connected')
        elif msg['msg_type'] == 'data:update':
            # Parse comma separated data record
            data = dict(zip(['timestamp'] + self.COLS, msg['value'].split(',')))
            for key, value in data.items():
                try:
                    data[key] = ast.literal_eval(value) if value else None
                except (SyntaxError, ValueError):
                    pass
            return data
        elif msg['msg_type'] == 'data:error':
            logger.error(msg['value'])
            await socket.close()

    async def stream(self):
        async with aiohttp.ClientSession() as session:
            # ping 10s
            print("streaming open")
            while True:
                async with session.ws_connect(STREAMING_BASE_URL + 'streaming/', heartbeat=5) as ws:
                    await ws.send_json({
                        'msg_type': 'data:subscribe_oauth',
                        'value': ','.join(self.COLS),
                        'token': self.tesla.token["access_token"],
                        'tag': str(self['vehicle_id'])
                    })
                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.BINARY:
                            parsed = await self._parse_msg(ws, msg)
                            if parsed:
                                yield parsed
                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            break
                await asyncio.sleep(5)

    async def api(self, name, **kwargs):
        """ Endpoint request with vehicle_id path variable """
        api_response = await self.tesla.api(name, {'vehicle_id': self['id_s']}, **kwargs)
        api_error = api_response.get("error", None)

        if api_error:
            if "vehicle unavailable" in api_error:
                raise VehicleAsleep()
            elif '"timeout"' in api_error:
                raise VehicleTimeout()
            else:
                raise VehicleError(api_error)

        return await self.tesla.api(name, {'vehicle_id': self['id_s']}, **kwargs)

    async def command(self, name, **kwargs):
        """ Wrapper method for vehicle command response error handling """
        api_response = await self.api(name, **kwargs)

        response = api_response["response"]

        if not response.get('result', None):
            raise VehicleError(response['reason'])

        return response['result']


class AsyncTesla(AsyncOAuth2Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, update_token=self._update_token)
        self.redis = get_redis()
        self.endpoints = {}

    @classmethod
    async def create(cls, *args, **kwargs):
        tesla = cls(*args, **kwargs)
        await tesla.load_token()
        return tesla

    async def _update_token(self, token: dict, refresh_token: str):
        self.redis.hset("tesla:token", mapping=token)

    def refresh_token(self, url, refresh_token=None, body='', auth=None, headers=None, **kwargs):
        session_kwargs = self._extract_session_request_params(kwargs)
        body = dict(
            grant_type="refresh_token",
            client_id="ownerapi",
            refresh_token=refresh_token or self.token.get("refresh_token"),
            scope="openid email offline_access",
        )
        body.update(kwargs)

        if headers is None:
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }

        return self._refresh_token(
            url, refresh_token=refresh_token, body=body, headers=headers,
            auth=auth, **session_kwargs)

    async def _refresh_token(self, url, refresh_token=None, body='',
                             headers=None, auth=USE_CLIENT_DEFAULT, **kwargs):
        resp = await self.post(
            url, json=body, headers=headers,
            auth=auth, **kwargs)

        for hook in self.compliance_hook['refresh_token_response']:
            resp = hook(resp)

        resp.raise_for_status()
        token = self.parse_response_token(resp.json())
        if 'refresh_token' not in token:
            self.token['refresh_token'] = refresh_token

        if self.update_token:
            await self.update_token(self.token, refresh_token=refresh_token)


    async def load_token(self) -> dict:
        token = self.redis.hgetall("tesla:token")

        if token:
            token["expires_in"] = int(token["expires_in"])
            token["expires_at"] = int(token["expires_at"])
            self.token = token
        else:
            await self.refresh_token(
                SSO_BASE_URL + 'oauth2/v3/token',
                os.environ["TESLA_TOKEN"]
            )

    @property
    async def vehicles(self) -> List[Vehicle]:
        r = await self.api("VEHICLE_LIST")
        return [Vehicle(x, self) for x in r["response"]]

    async def api(self, name, path_vars=None, **kwargs):
        """ Convenience method to perform API request for given endpoint name,
        with keyword arguments as parameters. Substitutes path variables in URI
        using path_vars. Raises ValueError if endpoint name is not found.
        Return type: dict or String
        """
        path_vars = path_vars or {}
        # Load API endpoints once
        if not self.endpoints:
            try:
                data = pkgutil.get_data(__name__, 'endpoints.json')
                self.endpoints = json.loads(data.decode())
                logger.debug('%d endpoints loaded', len(self.endpoints))
            except (IOError, ValueError):
                logger.error('No endpoints loaded')
        # Lookup endpoint name
        try:
            endpoint = self.endpoints[name]
        except KeyError:
            raise ValueError('Unknown endpoint name ' + name)
        # Fetch token if not authorized and API requires authorization
        # if endpoint['AUTH'] and not self.authorized:
        #     self.fetch_token()
        # Substitute path variables in URI
        try:
            uri = API_BASE_URL + endpoint['URI'].format(**path_vars)
        except KeyError as e:
            raise ValueError('%s requires path variable %s' % (name, e))
        # Perform request using given keyword arguments as parameters
        arg_name = 'params' if endpoint['TYPE'] == 'GET' else 'json'
        serialize = endpoint.get('CONTENT') != 'HTML' and name != 'STATUS'
        request = await self.request(
            method=endpoint['TYPE'],
            url=uri,
            **{arg_name: kwargs}
        )

        if serialize:
            response = request.json()
            return response
        else:
            return request.text
