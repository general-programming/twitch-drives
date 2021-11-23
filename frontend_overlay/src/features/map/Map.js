import { useSelector } from "react-redux";
import { selectDriveInfo } from "../driveinfo/driveInfoSlice";
import {
    MapContainer,
    TileLayer,
    Marker,
    useMap,
} from "@monsonjeremy/react-leaflet";
import styles from "./Map.module.css";

import "leaflet/dist/leaflet.css";
import * as L from "leaflet";

// Setup map
// delete L.Icon.Default.prototype._getIconUrl;

// L.Icon.Default.mergeOptions({
//     iconRetinaUrl: require("leaflet/dist/images/marker-icon-2x.png").default,
//     iconUrl: require("leaflet/dist/images/marker-icon.png").default,
//     shadowUrl: require("leaflet/dist/images/marker-shadow.png").default,
// });

const arrowIcon = L.divIcon({
    className: 'icon-arrow',
    html: '<svg viewBox="0 0 32 32" height="32" width="32"><path style="fill: #9146ff" d="m 15.992188,2 a 1.0001,1.0001 0 0 0 -0.914063,0.6113281 l -11,25.9999999 A 1.0001,1.0001 0 0 0 5.5371094,29.84375 L 16,23.185547 26.462891,29.84375 a 1.0001,1.0001 0 0 0 1.458984,-1.232422 l -11,-25.9999999 A 1.0001,1.0001 0 0 0 15.992188,2 Z" /></svg>',
    iconSize: [32, 32],
    iconAnchor: [16, 16],
});

const mapboxToken =
    "pk.eyJ1IjoibmVwZWF0IiwiYSI6ImNrdnVmYWZrOTVhNGQydW51aTZ0eHVpYmcifQ.16at8c1_HQ2xUmMn1R3JBQ";
const startZoom = 15;

function ChangeView({ latitude, longitude, heading, marker }) {
    const map = useMap();
    const location = new L.LatLng(latitude, longitude);
    map.panTo(location);
    try {
        document.getElementsByClassName("icon-arrow")[0].children[0].style["transform"] = `rotate(${heading}deg)`
    } catch (e) { }
    // mapMarker.setLatLng(location)

    return marker;
}

export function Map() {
    const info = useSelector(selectDriveInfo);
    const position = [info.latitude, info.longitude];
    const marker = <Marker position={position} icon={arrowIcon} />;

    return (
        <MapContainer
            className={styles.map}
            center={position}
            zoom={startZoom}
            zoomControl={false}
            attributionControl={false}
        >
            <TileLayer
                attribution='Map data &copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> contributors, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>'
                url="https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}"
                maxZoom={18}
                id="mapbox/streets-v11"
                tileSize={512}
                zoomOffset={-1}
                accessToken={mapboxToken}
            />

            <ChangeView latitude={info.latitude} longitude={info.longitude} heading={info.heading} marker={marker} />
        </MapContainer>
    );
}
