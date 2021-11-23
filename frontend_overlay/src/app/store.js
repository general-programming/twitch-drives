import { configureStore } from "@reduxjs/toolkit";
import driveInfoReducer from "../features/driveinfo/driveInfoSlice";
import chatReducer from "../features/chat/chatSlice";

export const store = configureStore({
    reducer: {
        driveInfo: driveInfoReducer,
        chat: chatReducer,
    },
});
