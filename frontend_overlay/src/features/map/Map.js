import { useSelector } from 'react-redux';
import { selectDriveInfo } from '../driveinfo/driveInfoSlice';
import { MapContainer, TileLayer, Marker, Popup, useMap } from '@monsonjeremy/react-leaflet'
import styles from './Map.module.css';

import "leaflet/dist/leaflet.css";
import * as L from "leaflet";

// Setup map
delete L.Icon.Default.prototype._getIconUrl;

L.Icon.Default.mergeOptions({
    iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png').default,
    iconUrl: require('leaflet/dist/images/marker-icon.png').default,
    shadowUrl: require('leaflet/dist/images/marker-shadow.png').default
});

const mapboxToken =
    "pk.eyJ1IjoibmVwZWF0IiwiYSI6ImNrdnVmYWZrOTVhNGQydW51aTZ0eHVpYmcifQ.16at8c1_HQ2xUmMn1R3JBQ";
const startPoint = [47.4720469201162, -122.22098071564105];
const startZoom = 15;

// if (isExisting(event.latitude) && isExisting(event.longitude)) {
//     const location = new L.LatLng(event.latitude, event.longitude)
//     map.panTo(location);
//     mapMarker.setLatLng(location)
// }

function ChangeView({ latitude, longitude }) {
    const map = useMap();
    const location = new L.LatLng(latitude, longitude)
    map.panTo(location);
    // mapMarker.setLatLng(location)

    return null;
}

export function Map() {
    const info = useSelector(selectDriveInfo);
    const position = [info.latitude, info.longitude];

    return <MapContainer className={styles.map} center={position} zoom={startZoom} zoomControl={false} attributionControl={false}>
        <TileLayer
            attribution='Map data &copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> contributors, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>'
            url='https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}'
            maxZoom={18}
            id='mapbox/streets-v11'
            tileSize={512}
            zoomOffset={-1}
            accessToken={mapboxToken}
        />
        <Marker position={position} />
        <ChangeView latitude={info.latitude} longitude={info.longitude} />
    </MapContainer>;
}
