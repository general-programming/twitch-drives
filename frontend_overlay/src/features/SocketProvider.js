import React, { createContext, useState, useEffect } from 'react';
import { useDispatch } from 'react-redux';
import { socketUpdate } from './driveinfo/driveInfoSlice';
import { addMessage } from './chat/chatSlice';

export default function SocketProvider({ children }) {
    const dispatch = useDispatch();
    const [serial, setSerial] = useState(0);

    useEffect(() => {
        let socket = new WebSocket("ws://79.110.170.251:8000/stream");
        socket.onopen = (event) => {
            console.log("socket opened", event);
        };
        socket.onclose = (event) => {
            console.log("socket closed", event);
            setSerial(x => x+1); // trigger re-render
        };

        socket.onmessage = event => {
            const data = JSON.parse(event.data);
            if (data.chat) {
                dispatch(addMessage(data.chat));
            } else {
                dispatch(socketUpdate(data));
            }
        };

        return () => socket.close();
    }, [serial]);

    return children;
};
