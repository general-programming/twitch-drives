import React, { createContext, useState, useEffect } from 'react'
import { useDispatch } from 'react-redux';
import { socketUpdate } from './driveinfo/driveInfoSlice';
import { addMessage } from './chat/chatSlice';

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

function createSocket(dispatch, onMessage) {
    // socket = new WebSocket("ws://" + document.location.host + "/stream");
    let socket = new WebSocket("ws://79.110.170.251:8000/stream");
    socket.onopen = onOpen;
    socket.onmessage = onMessage;
    socket.onclose = (event) => {
        console.log("socket closed", event);
        if (event.code !== 4269) {
            setTimeout(() => createSocket(dispatch, onMessage), 1000);
        }
    };

    return socket;
}

const SocketProvider = ({ children }) => {
    const dispatch = useDispatch();
    const [socket, setSocket] = useState(0);

    useEffect(() => {
        let socket = createSocket(dispatch, (event) => onMessage(dispatch, event));

        return () => {
            socket.close(4269);
        }
    });

    return children;
};

export default SocketProvider;
