import "./Raport.scss";

import { useState, useEffect } from "preact/hooks";
import ProgressBar from "./ProgressBar/ProgressBar";
import useWebSocket from "../../hooks/useWebSocket";
import ConnectionIndicator from "./ConnectionIndicator/ConnectionIndicator";
import type { FnData, AlgorithmData, ParamTypes } from "../../interfaces";
import NotificationManager from "./NotificationManager/NotificationManager";

interface Props {
    selectedFnData: FnData;
    algorithmsData: AlgorithmData[];
    sharedAlgsParams: ParamTypes[];
}

// TODO: Validacja form + funkcja
// TODO: Pobieranie aktualnego stanu z serwera
// TODO: Wyśweitlanie raportu
const Raport = ({ selectedFnData, algorithmsData, sharedAlgsParams }: Props) => {
    const [notifyData, setNotifyData] = useState({ msg: "", color: "", id: 0 });
    const { lastMessage, sendMessage, readyState, retryCount } = useWebSocket(
        "ws://localhost:8000/ws"
    );

    const [isAwaitServerResponse, setIsAwaitServerResponse] = useState(false)

    const [isPaused, setIsPaused] = useState<boolean>(false);
    const [isStarted, setIsStarted] = useState<boolean>(false);
    const [progress, setProgress] = useState<number>(0);

    const addNewNotification = (message:string, color:string) => {
        setNotifyData({
            msg: message,
            color: color,
            id: Date.now() // Zmiana ID wywoła useEffect w NotificationManager
        });
    };

    // const [logs, setLogs] = useState<string[]>([]);
    useEffect(() => {
        setIsAwaitServerResponse(false)
        switch (lastMessage?.type) {
            case "start":
                setIsStarted(true);
                addNewNotification("Started successfully", "green" )
                break;
            case "pause":
                setIsPaused(!isPaused);
                addNewNotification( "Paused successfully", "green" )
                break;

            case "stop":
                setIsPaused(false);
                setIsStarted(false)
                addNewNotification( "Stopped successfully", "green" )
                break;
            case "progress":
                setProgress(+lastMessage.message);
                break;

            case "finished":
                setIsPaused(false);
                setIsStarted(false);
                if (typeof lastMessage.message == "string"){
                    addNewNotification(lastMessage.message, "green")
                 
                }
                
                break;

            default:
                console.log("Otrzymano wiadomość: ", lastMessage);
        }
    }, [lastMessage]);

    const getStartInfo = () => {
        let algorithms = algorithmsData.filter((algParams) => algParams.isUsed)

        const updatedAlgorithms = algorithms.map(alg => ({
        ...alg,
        args: [ ...alg.args, ...sharedAlgsParams ]
        }));
        
        return { 
            type: "start",
            selected_function: selectedFnData,
            algorithms: updatedAlgorithms
        }
    };

    const sendAndShowNotification = (data: any, infoForUser: string) =>{
        if( ! isAwaitServerResponse){
            setIsAwaitServerResponse(true)
            addNewNotification(infoForUser, "orange")
            sendMessage(data)
        }
    }
    
    
    return (
        <div className="Raport">
   
            <h2>Raport:</h2>
            <div className="Raport__btnsBox">
                <button
                    onClick={() =>  sendAndShowNotification(getStartInfo(), "Trwa uruchamianie")}
                    disabled={isStarted}
                    className="Raport__btn Raport__btn--start"
                >
                    <svg
                        width="20"
                        height="20"
                        viewBox="0 0 24 24"
                        fill="currentColor"
                    >
                        <polygon points="5 3 19 12 5 21 5 3"></polygon>
                    </svg>
                    Start
                </button>
                <button
                    onClick={() =>  sendAndShowNotification({ type: "pause" }, "Trwa pauzowanie")}
                    disabled={!isStarted}
                    className="Raport__btn Raport__btn--pause"
                >
                    {isPaused ? (
                        <>
                            <svg
                                width="20"
                                height="20"
                                viewBox="0 0 24 24"
                                fill="currentColor"
                            >
                                <polygon points="5 3 19 12 5 21 5 3"></polygon>
                            </svg>
                            Continue
                        </>
                    ) : (
                        <>
                            <svg
                                width="20"
                                height="20"
                                viewBox="0 0 24 24"
                                fill="currentColor"
                            >
                                <rect x="6" y="4" width="4" height="16"></rect>
                                <rect x="14" y="4" width="4" height="16"></rect>
                            </svg>
                            Pause
                        </>
                    )}
                </button>
                <button
                    onClick={() =>  sendAndShowNotification({ type: "stop" }, "Trwa zatrzymywanie")}
                    disabled={!isStarted}
                    className="Raport__btn Raport__btn--stop"
                >
                    <svg
                        width="20"
                        height="20"
                        viewBox="0 0 24 24"
                        fill="currentColor"
                    >
                        <rect x="3" y="3" width="18" height="18"></rect>
                    </svg>
                    Stop
                </button>
            </div>

            {isStarted && (
                <div id="progress-container" class="progress-container hidden">
                    <ProgressBar
                        label="Algorytmy"
                        progress={progress}
                        isComplete={false}
                    />
                </div>
            )}

            <div className="Raport__result">
                <h4>Wybrana funkcja:</h4>
                <pre>{JSON.stringify(selectedFnData, null, 2)}</pre>
                <br />
                <br />
                <br />
                <h4>Wspólne parametry</h4>
                <pre>{JSON.stringify(sharedAlgsParams, null, 2)}</pre>

                <br />
                <br />
                <br />
                <h4>Parametry algorytmów:</h4>
                <pre>
                    {JSON.stringify(
                        algorithmsData.filter((algParams) => algParams.isUsed),
                        null,
                        2
                    )}
                </pre>
            </div>
            <ConnectionIndicator status={readyState} />
            <NotificationManager 
                newMessage={notifyData.msg} 
                color={notifyData.color} 
                id={notifyData.id} 
            />
        </div>
    );
};

export default Raport;
