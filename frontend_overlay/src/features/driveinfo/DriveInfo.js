import { useSelector } from 'react-redux';
import { selectDriveInfo } from './driveInfoSlice';
import styles from './DriveInfo.module.css';

const SHIFT_STATES = {
    P: "park",
    R: "reverse",
    N: "neutral",
    D: "drive",
};

export function DriveInfo() {
    const info = useSelector(selectDriveInfo);
    console.log(info);

    const shifters = [];
    Object.keys(SHIFT_STATES).map(key => {
        let shiftName = SHIFT_STATES[key];
        const shiftClasses = [];
        if (info.shift_state == key) {
            shiftClasses.push(styles.active);
        }
        shifters.push(
            <li key={key} name={shiftName} className={shiftClasses}> {shiftName.toUpperCase()}</li>
        );
    });

    return (<section className={styles.info}>
        <ul className={styles.shifter}>
            {shifters}
        </ul>
        <div className={styles.speedInfo}>
            <p id="speed" className={styles.speed}>{info.speed}</p>
            <p className={styles.unit}>MPH</p>
        </div>
    </section>);
}
