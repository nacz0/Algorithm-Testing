import { useState, useEffect } from 'preact/hooks';
import ProgressBar from './components/ProgressBar/ProgressBar';
import ConnectionIndicator from './components/ConnectionIndicator/ConnectionIndicator';
import NotificationManager from './components/NotificationManager/NotificationManager';
import AlgorytmsSection from './components/AlogrytmsSection/AlogrytmsSection.tsx';
import CustomFnSection from './components/CustomFnSection/FnSection.tsx';
import ControlPanel from './components/ControlPanel/ControlPanel.tsx';
import './app.css';

import useWebSocket from './hooks/useWebSocket.tsx';
import { SharedParamsSection } from './components/SharedParamsSection/SharedParamsSection.tsx';
import type { AlgorithmData, FnData, ParamTypes } from './interfaces.ts';
import Raport from './components/Raport/Raport.tsx';

export function App() {
    const [selectedFnData, setSelectedFnData] = useState<FnData>({ name: '', code: '', isCustom: false, bounds: [0, 0] });
    const [functionsData, setFunctionsData] = useState<FnData[]>([]);
    const [algorithmsData, setAlgorithmsData] = useState<AlgorithmData[]>([]);
    const [sharedAlgsParams, setSharedAlgsParams] = useState<ParamTypes[]>([]);
    const [notifyData, setNotifyData] = useState({ msg: '', color: '', id: 0 });
    const [results, setResults] = useState<any>({ result: {}, figures: [] });

    const [isPaused, setIsPaused] = useState<boolean>(false);
    const [isStarted, setIsStarted] = useState<boolean>(false);
    const [algProgress, setAlgProgress] = useState<number>(0);
    const [progress, setProgress] = useState<number>(0);

    const { lastMessage, sendMessage, readyState, retryCount } = useWebSocket('ws://localhost:8000/ws');

    const addNewNotification = (message: string, color: string) => {
        setNotifyData({
            msg: message,
            color: color,
            id: Date.now(), // Zmiana ID wywoła useEffect w NotificationManager
        });
    };

    useEffect(() => {
        switch (lastMessage?.type) {
            case 'start':
                setIsStarted(true);
                setIsPaused(false);
                addNewNotification('Started successfully', 'green');
                setAlgProgress(0);
                setProgress(0);
                setResults({ result: {}, figures: {} });
                break;
            case 'pause':
                console.log('pause');
                setIsPaused(true);
                console.log('Pause', isStarted, isPaused);
                addNewNotification('Paused successfully', 'green');
                break;

            case 'stop':
                console.log('stop');
                setIsPaused(false);
                setIsStarted(false);
                addNewNotification('Stopped successfully', 'green');
                break;
            case 'progress':
                const type = lastMessage.message.type;
                if (type === 'alg_progress') {
                    setAlgProgress(lastMessage.message.progress);
                } else if (type === 'param_progress') {
                    setProgress(lastMessage.message.progress);
                }
                break;

            case 'finished':
                setIsPaused(false);
                setIsStarted(false);

                addNewNotification('Finished', 'green');
                console.log(lastMessage.message.figures.length);

                setResults(lastMessage.message);
                break;

            case 'error':
                setIsPaused(false);
                setIsStarted(false);

                addNewNotification('Wrong function syntax', 'red');
                // setResults(lastMessage.message);
                break;

            case 'get_params':
                if (localStorage.getItem('algorithmsData') == null) {
                    setAlgorithmsData(lastMessage.message.algorithms as AlgorithmData[]);
                } else {
                    setAlgorithmsData(JSON.parse(localStorage.getItem('algorithmsData') || '[]'));
                }
                if (localStorage.getItem('sharedAlgsParams') == null) {
                    setSharedAlgsParams(lastMessage.message.shared_params);
                } else {
                    setSharedAlgsParams(JSON.parse(localStorage.getItem('sharedAlgsParams') || '[]'));
                }

                if (localStorage.getItem('functionsData') == null) {
                    setFunctionsData(lastMessage.message.functions_data as FnData[]);
                } else {
                    setFunctionsData(JSON.parse(localStorage.getItem('functionsData') || '[]'));
                    setSelectedFnData(JSON.parse(localStorage.getItem('functionsData') || '[]')[0]);
                }

                setAlgProgress(lastMessage.message.progressInfo.alg_progress);
                setProgress(lastMessage.message.progressInfo.param_progress);

                setIsPaused(lastMessage.message.isPaused);
                setIsStarted(lastMessage.message.isStarted);
                // setFunctionsData(lastMessage.message.functions_data as FnData[]);
                // setSelectedFnData(lastMessage.message.function_data[0] as FnData);

                break;

            default:
                console.log('Otrzymano wiadomość: ', lastMessage);
        }
    }, [lastMessage]);

    useEffect(() => {
        if (algorithmsData.length != 0) localStorage.setItem('algorithmsData', JSON.stringify(algorithmsData));
    }, [algorithmsData]);

    useEffect(() => {
        if (sharedAlgsParams.length != 0) localStorage.setItem('sharedAlgsParams', JSON.stringify(sharedAlgsParams));
    }, [sharedAlgsParams]);

    useEffect(() => {
        if (functionsData.length != 0) localStorage.setItem('functionsData', JSON.stringify(functionsData));
    }, [functionsData]);

    useEffect(() => {
        if (readyState === 'OPEN') {
            sendMessage({ type: 'get_params' });
        }
    }, [readyState]);

    const sendAndShowNotification = (type: string, infoForUser: string) => {
        const data = {
            type: type,
            algorithmsData: algorithmsData,
            shared_params: sharedAlgsParams,
            selected_function: selectedFnData,
        };

        addNewNotification(infoForUser, 'orange');
        sendMessage(data);
    };

    return (
        <div>
            <ConnectionIndicator status={readyState} />
            <NotificationManager newMessage={notifyData.msg} color={notifyData.color} id={notifyData.id} />
            <h1>Testowanie algorytmów heurystycznych</h1>
            <CustomFnSection isStarted={isStarted} setFn={setSelectedFnData} selectedFn={selectedFnData} fnsData={functionsData || []} />
            <SharedParamsSection isStarted={isStarted} sharedAlgsParams={sharedAlgsParams} setSharedAlgsParams={setSharedAlgsParams} />
            <AlgorytmsSection isStarted={isStarted} algorithmData={algorithmsData} setAlgorithmData={setAlgorithmsData} />
            <ControlPanel sendAndShowNotification={sendAndShowNotification} isStarted={isStarted} isPaused={isPaused} />
            {isStarted && (
                <div id="progress-container" className="progress-container hidden">
                    <ProgressBar label="Algorytmy" progress={algProgress} />
                    <ProgressBar label="Strojenie" progress={progress} />
                </div>
            )}
            {Object.keys(results.figures).length > 0 && <Raport results={results} />}
        </div>
    );
}

//TODO: przy update progress zapisuj stan do manager + wysyłaj z get_params
