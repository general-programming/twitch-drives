import React, { createContext } from 'react'
import { useDispatch } from 'react-redux';
import { socketUpdate } from './driveinfo/driveInfoSlice';
import { addMessage } from './chat/chatSlice';

const WebSocketContext = createContext(null)

export { WebSocketContext }

const onOpen = (event) => {
    console.log("socket opened", event);
}

const onMessage = (dispatch, event) => {
    const data = JSON.parse(event.data);
    if (data.chat) {
        dispatch(addMessage(data.chat));
    } else {
        dispatch(socketUpdate(data));
    }
}

const SocketProvider = ({ children }) => {
    let socket;
    let ws;
    const dispatch = useDispatch();

    function createSocket() {
        // socket = new WebSocket("ws://" + document.location.host + "/stream");
        socket = new WebSocket("ws://79.110.170.251:8000/stream");
        socket.onopen = onOpen;
        socket.onmessage = (event) => onMessage(dispatch, event);
        socket.onClose = () => {
            console.log("socket closed");
            setTimeout(createSocket, 1000);
        };

        ws = {
            socket: socket,
        }
    }

    if (!socket) {
        createSocket();
    }

    return (
        <WebSocketContext.Provider value={ws}>
            {children}
        </WebSocketContext.Provider>
    )
};

export default SocketProvider;
