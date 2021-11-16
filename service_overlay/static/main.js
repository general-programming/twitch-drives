const speedElement = document.getElementById("speed");
const batteryPercentElement = document.getElementById("battery-percent");
const batteryLeftElement = document.getElementById("battery-left");
const batteryRightElement = document.getElementById("battery-right");
const SHIFTER_MAP = {
    P: "park",
    R: "reverse",
    N: "neutral",
    D: "drive",
};

const isExisting = (data) => {
    if (typeof data === "undefined" || data === null) {
        return false
    }
    return true;
}

// Setup map
const mapboxToken =
"pk.eyJ1IjoibmVwZWF0IiwiYSI6ImNrdnVmYWZrOTVhNGQydW51aTZ0eHVpYmcifQ.16at8c1_HQ2xUmMn1R3JBQ";
const startPoint = [47.4720469201162, -122.22098071564105];
const startZoom = 15;

const map = L.map("map", {
    center: startPoint,
    zoom: startZoom,
    zoomControl: false,
    // Please put this in the channel description or anywhere else visible.
    // Map data © OpenStreetMap contributors, Imagery © Mapbox, powered by Leaflet
    attributionControl: false,
});

L.tileLayer(
"https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}",
{
  attribution:
    'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> contributors, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
  maxZoom: 18,
  id: "mapbox/streets-v11",
  tileSize: 512,
  zoomOffset: -1,
  accessToken: mapboxToken
}
).addTo(map);

const arrowIcon = L.divIcon({
    className: 'icon-arrow',
    html: '<svg viewBox="0 0 32 32" height="32" width="32"><path style="fill: #9146ff" d="m 15.992188,2 a 1.0001,1.0001 0 0 0 -0.914063,0.6113281 l -11,25.9999999 A 1.0001,1.0001 0 0 0 5.5371094,29.84375 L 16,23.185547 26.462891,29.84375 a 1.0001,1.0001 0 0 0 1.458984,-1.232422 l -11,-25.9999999 A 1.0001,1.0001 0 0 0 15.992188,2 Z" /></svg>',
    iconSize: [32, 32],
    iconAnchor: [16, 16],
});

const mapMarker = L.marker(map.getCenter(), {icon: arrowIcon}).addTo(map);

// Setup websocket
const parseEvent = (event) => {
    if (isExisting(event.speed)) {
        console.log("speed", event.speed);
        speedElement.textContent = event.speed;
    }

    if (isExisting(event.battery)) {
        console.log("battery", event.battery);
        batteryPercentElement.textContent = `${event.battery}% | ${event.range}mi`;
        batteryLeftElement.style.width = `${event.battery}%`;
        batteryRightElement.style.width = `${100 - event.battery}%`;
    }

    if (isExisting(event.shift_state)) {
        console.log("shift state", event.shift_state);
        // clear existing shifter
        try {
            document.querySelector(".shifter .active").classList.remove("active");
        } catch(e) {}

        // find the shifter and activate it
        const shifterName = SHIFTER_MAP[event.shift_state];
        document.querySelector(`.shifter li[name=${shifterName}]`).classList.add("active");
    }

    if (isExisting(event.latitude) && isExisting(event.longitude)) {
        const location = new L.LatLng(event.latitude, event.longitude)
        map.panTo(location);
        mapMarker.setLatLng(location)
    }

    if (isExisting(event.heading)) {
        mapMarker._icon.children[0].style.transform = `rotate(${event.heading}deg)`;
    }

    if (isExisting(event.chat)) {
        parseChat(event.chat);
    }
}

let parseChat = (chat) => {
    const chatElement = document.getElementById("chat");
    if (chatElement.childElementCount == 20) {
        chatElement.childNodes[0].remove()
    }
    let newElement = document.createElement("li");
    newElement.textContent = `[${chat.source}/${chat.channel}] ${chat.username}: ${chat.message}`
    chatElement.appendChild(newElement);
}

const launch_socket = () => {
    let sock = new WebSocket("ws://" + document.location.host + "/stream");

    sock.onopen = (event) => {
        console.log("socket opened", event);
    }

    sock.onmessage = (event) => {
        let data = JSON.parse(event.data);
        console.log(data);
        parseEvent(data);
    }

    sock.onclose = () => {
        console.log("socket closed");
        setTimeout(launch_socket, 1000);
    }
}

launch_socket();
