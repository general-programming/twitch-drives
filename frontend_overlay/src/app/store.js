import { configureStore } from '@reduxjs/toolkit';
import counterReducer from '../features/counter/counterSlice';
import driveInfoReducer from '../features/driveinfo/driveInfoSlice';
import chatReducer from '../features/chat/chatSlice';

export const store = configureStore({
    reducer: {
        counter: counterReducer,
        driveInfo: driveInfoReducer,
        chat: chatReducer,
    },
});
