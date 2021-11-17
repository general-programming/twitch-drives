import { createSlice } from '@reduxjs/toolkit';

const initialState = {
    messages: []
};

export const chatSlice = createSlice({
    name: 'chat',
    initialState,
    // The `reducers` field lets us define reducers and generate associated actions
    reducers: {
        addMessage: (state, action) => {
            let message = action.payload;
            if (state.messages.length === 10) {
                state.messages.shift();
            }
            state.messages.push(message);
        },
    },
});

export const { addMessage } = chatSlice.actions;

export const selectChat = (state) => state.chat.messages;

export default chatSlice.reducer;
