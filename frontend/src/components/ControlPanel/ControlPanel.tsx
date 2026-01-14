import './ControlPanel.scss';

interface Props {
    sendAndShowNotification: (data: any, infoForUser: string) => void;
    isStarted: boolean;
    isPaused: boolean;
}

const ControlPanel = ({ sendAndShowNotification, isStarted, isPaused }: Props) => {
    return (
        <div className="Raport__btnsBox">
            <button onClick={() => sendAndShowNotification('start', 'Trwa uruchamianie')} disabled={isStarted} className="Raport__btn Raport__btn--start">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                    <polygon points="5 3 19 12 5 21 5 3"></polygon>
                </svg>
                Start
            </button>
            <button
                onClick={() => sendAndShowNotification(isPaused ? 'start' : 'pause', isPaused ? 'Trwa wznawianie' : 'Trwa pauzowanie')}
                disabled={!isStarted}
                className="Raport__btn Raport__btn--pause"
            >
                {isPaused ? (
                    <>
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                            <polygon points="5 3 19 12 5 21 5 3"></polygon>
                        </svg>
                        Kontynuuj
                    </>
                ) : (
                    <>
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                            <rect x="6" y="4" width="4" height="16"></rect>
                            <rect x="14" y="4" width="4" height="16"></rect>
                        </svg>
                        Pauza
                    </>
                )}
            </button>
            <button onClick={() => sendAndShowNotification('stop', 'Trwa zatrzymywanie')} disabled={!isStarted} className="Raport__btn Raport__btn--stop">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                    <rect x="3" y="3" width="18" height="18"></rect>
                </svg>
                Stop
            </button>
        </div>
    );
};

export default ControlPanel;
