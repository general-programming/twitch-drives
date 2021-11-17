import { createSlice } from '@reduxjs/toolkit';

const initialState = {
    battery: 100,
    range: 0,
    heading: 0,
    latitude: 0,
    longitude: 0,
    speed: 0,
    shift_state: 'P',
    odometer: 0,
    timestamp: 0
};

export const driveInfoSlice = createSlice({
    name: 'driveInfo',
    initialState,
    // The `reducers` field lets us define reducers and generate associated actions
    reducers: {
        socketUpdate: (state, action) => {
            let event = action.payload;
            for (const [key, value] of Object.entries(event)) {
                state[key] = value;
            }
        },
    },
});

export const { socketUpdate } = driveInfoSlice.actions;

export const selectDriveInfo = (state) => state.driveInfo;

export default driveInfoSlice.reducer;
