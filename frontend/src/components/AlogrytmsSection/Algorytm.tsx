import type { AlgorithmData } from '../../interfaces';
import './Algorytm.scss';

interface Props {
    algorithmData: AlgorithmData;
    setAlgorithmData: (callback: (a: AlgorithmData[]) => AlgorithmData[]) => void;
    algIndex: number;
    isStarted: boolean;
}

// Ulepszona walidacja: tylko liczby i jedna kropka z max 5 miejscami po przecinku
const validateAndCleanInput = (value: string, type: 'int' | 'float'): string => {
    console.log(value, type);

    if (type === 'int') {
        return value.replace(/[^0-9]/g, '');
    } else {
        // Pozwala na cyfry i jedną kropkę
        let cleaned = value.replace(/[^0-9.]/g, '');
        // Zapobiega wpisaniu więcej niż jednej kropki
        const parts = cleaned.split('.');
        if (parts.length > 2) {
            cleaned = parts[0] + '.' + parts.slice(1).join('');
        }
        // Ograniczenie do 5 miejsc po przecinku
        if (parts[1] && parts[1].length > 5) {
            cleaned = parts[0] + '.' + parts[1].slice(0, 5);
        }
        return cleaned;
    }
};

const Alogrytm = ({ algorithmData, setAlgorithmData, algIndex, isStarted }: Props) => {
    const changeParam = (paramIndex: number, type: 'min' | 'max' | 'value', value: string, paramType: 'int' | 'float') => {
        console.log(value);

        const cleanedValue = validateAndCleanInput(value, paramType);

        setAlgorithmData((algsParams) => {
            const algsParamsCopy = JSON.parse(JSON.stringify(algsParams));
            // Zapisujemy jako string w stanie, aby kropka nie znikała podczas pisania
            // Jeśli Twoje interfejsy WYMAGAJĄ number, użyj parseFloat(cleanedValue)
            // ale pamiętaj, że to utrudni wpisywanie samej kropki.
            algsParamsCopy[algIndex].params[paramIndex][type] = cleanedValue;
            return algsParamsCopy;
        });
    };

    const toggleState = () => {
        setAlgorithmData((algsParams) => {
            const algsParamsCopy = JSON.parse(JSON.stringify(algsParams));
            algsParamsCopy[algIndex].isUsed = !algsParamsCopy[algIndex].isUsed;
            return algsParamsCopy;
        });
    };

    return (
        <div className="algorithm-card">
            <div className="algorithm-header">
                <h3>{algorithmData.name} algorytm</h3>
                <div onClick={() => !isStarted && toggleState()} className={`toggle-switch ${algorithmData.isUsed ? 'active' : ''}`}>
                    <div className="toggle-slider"></div>
                </div>
            </div>

            {algorithmData.params.length === 0 ? (
                'Brak argumentów'
            ) : (
                <>
                    <div className="param-labels">
                        <div className="label-space"></div>
                        <div className="label-text">Min</div>
                        <div className="separator"></div>
                        <div className="label-text">Maks</div>
                    </div>

                    {algorithmData.params.map((param, index) => {
                        if ('value' in param) {
                            return (
                                <div className="param-row" key={index}>
                                    <label>{param.name}:</label>
                                    <input
                                        type="text" // Zmienione na text dla lepszej kontroli
                                        inputMode="decimal"
                                        onChange={(e) => changeParam(index, 'value', e.currentTarget.value, param.type)}
                                        value={param.value}
                                        disabled={isStarted}
                                        placeholder="0.00000"
                                    />
                                </div>
                            );
                        }

                        if ('min' in param) {
                            return (
                                <div className="param-row" key={index}>
                                    <label>{param.name}:</label>
                                    <input
                                        type="text"
                                        inputMode="decimal"
                                        onChange={(e) => changeParam(index, 'min', e.currentTarget.value, param.type)}
                                        value={param.min}
                                        disabled={isStarted}
                                    />
                                    <span className="separator">-</span>
                                    <input
                                        type="text"
                                        inputMode="decimal"
                                        onChange={(e) => changeParam(index, 'max', e.currentTarget.value, param.type)}
                                        value={param.max}
                                        disabled={isStarted}
                                    />
                                </div>
                            );
                        }
                        return null;
                    })}
                </>
            )}
        </div>
    );
};

export default Alogrytm;
