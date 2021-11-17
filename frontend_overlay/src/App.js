import React from "react";
import { Overlay } from "./features/overlay/Overlay";
import { DriveInfo } from "./features/driveinfo/DriveInfo";
import { BatteryInfo } from "./features/batteryinfo/BatteryInfo";
import { Chat } from "./features/chat/Chat";
import { Map } from "./features/map/Map";
import SocketProvider from "./features/SocketProvider";

function App() {
    return (
        <div className="App container">
            <SocketProvider>
                <DriveInfo />
                <BatteryInfo />
                <Chat />
                <Map />
            </SocketProvider>
        </div>
    );
}

export default App;
