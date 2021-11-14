const speedElement = document.getElementById("speed");
const SHIFTER_MAP = {
    P: "park",
    R: "reverse",
    N: "neutral",
    D: "drive",
};

let sock = new WebSocket("ws://" + document.location.host + "/stream");

sock.onopen = (event) => {
    console.log("socket opened", event);
}

sock.onmessage = (event) => {
    let data = JSON.parse(event.data);
    console.log(data);
    parseEvent(data);
}

const parseEvent = (event) => {
    if (event.speed) {
        console.log("speed", event.speed);
        speedElement.textContent = event.speed;
    }

    if (event.shift_state) {
        console.log("shift state", event.shift_state);
        // clear existing shifter
        try {
            document.querySelector(".shifter .active").classList.remove("active");
        } catch(e) {}

        // find the shifter and activate it
        const shifterName = SHIFTER_MAP[event.shift_state];
        document.querySelector(`.shifter li[name=${shifterName}]`).classList.add("active");
    }
}
