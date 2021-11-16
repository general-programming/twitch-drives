import { useSelector } from 'react-redux';
import { selectDriveInfo } from '../driveinfo/driveInfoSlice';
import styles from './BatteryInfo.module.css';

export function BatteryInfo() {
    const info = useSelector(selectDriveInfo);

    const leftStyle = {
        width: `${info.battery}%`
    };
    const rightStyle = {
        width: `${100 - info.battery}%`
    };

    return (<section>
        <p className={styles.percent}>{info.battery}% | {info.range}mi</p>
        <div className={styles.container}>
            <div className={styles.barLeft} style={leftStyle}></div>
            <div className={styles.barRight} style={rightStyle}></div>
        </div>
    </section>);
}
