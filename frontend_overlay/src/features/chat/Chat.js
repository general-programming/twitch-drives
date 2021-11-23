import { useSelector } from "react-redux";
import { selectChat } from "./chatSlice";
import styles from "./Chat.module.css";

export function Chat() {
    const messages = useSelector(selectChat);
    console.log(messages);

    return (
        <ul className={styles.chat}>
            {messages.map((msg) => {
                return (
                    <li className={styles[msg.source]}>
                        {msg.username} - {msg.message}
                    </li>
                );
            })}
        </ul>
    );
}
