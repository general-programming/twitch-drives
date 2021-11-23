import { useSelector } from "react-redux";
import { selectDriveInfo } from "./driveInfoSlice";
import styles from "./DriveInfo.module.css";

const SHIFT_STATES = {
    P: "PARK",
    R: "REVERSE",
    N: "NEUTRAL",
    D: "DRIVE",
};

export function DriveInfo() {
    const info = useSelector(selectDriveInfo);
    console.log(info);

    return (
        <section className={styles.info}>
            <ul className={styles.shifter}>
                {Object.keys(SHIFT_STATES).map((key) =>
                    <li key={key} name={SHIFT_STATES[key]} className={info.shift_state === key ? styles.active : null}>
                        {SHIFT_STATES[key]}
                    </li>
                )}
            </ul>
            <div className={styles.speedInfo}>
                <p id="speed" className={styles.speed}>
                    {info.speed}
                </p>
                <p className={styles.unit}>MPH</p>
            </div>
        </section>
    );
}
