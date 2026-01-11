import type { AlgorithmData } from '../../interfaces';
import './Algorytm.scss';

interface Props {
    algorithmData: AlgorithmData;
    setAlgorithmData: (a: AlgorithmData[]) => void;
    algIndex: number;
    isStarted: boolean;
}

const correctInputType = (e: any, type: 'int' | 'float') => {
    console.log(e.currentTarget.value, type);

    if (type === 'int') {
        e.currentTarget.value = e.currentTarget.value.replace(/[^0-9]/g, '');
    } else if (type === 'float') {
        e.currentTarget.value = e.currentTarget.value.replace(/[^0-9.]/g, '');
    }
};

const Alogrytm = ({ algorithmData, setAlgorithmData, algIndex, isStarted }: Props) => {
    const changeParam = (paramIndex: number, type: 'min' | 'max' | 'value', value: string) => {
        // @ts-ignore
        setAlgorithmData((algsParams) => {
            const algsParamsCopy = JSON.parse(JSON.stringify(algsParams));
            algsParamsCopy[algIndex].params[paramIndex][type] = Number(value);
            return algsParamsCopy;
        });
    };

    const toggleState = () => {
        // @ts-ignore
        setAlgorithmData((algsParams) => {
            const algsParamsCopy = JSON.parse(JSON.stringify(algsParams));
            algsParamsCopy[algIndex].isUsed = !algsParamsCopy[algIndex].isUsed;
            return algsParamsCopy;
        });
    };

    return (
        <div className="algorithm-card">
            <div className="algorithm-header">
                <h3>{algorithmData.name} algorithm</h3>
                <div onClick={() => !isStarted && toggleState()} className={`toggle-switch ${algorithmData.isUsed && 'active'}`} data-algo="bat">
                    <div className="toggle-slider"></div>
                </div>
            </div>

            {algorithmData.params.length == 0 ? (
                'Brak argumentów'
            ) : (
                <>
                    <div className="param-labels">
                        <div className="label-space"></div>
                        <div className="label-text">Min</div>
                        <div className="separator"></div>
                        <div className="label-text">Max</div>
                    </div>

                    {/* Wiersze parametrów (przykłady) */}

                    {algorithmData.params.map((param, index) => {
                        if ('value' in param) {
                            return (
                                <div className="param-row">
                                    <label>{param.name}:</label>
                                    <input
                                        onInput={(e) => correctInputType(e, param.type)}
                                        onChange={(e) => changeParam(index, 'value', e.currentTarget.value)}
                                        value={param.value}
                                        type="number"
                                        min={0}
                                        step={param.type == 'float' ? 0.1 : 1}
                                        disabled={isStarted}
                                    />
                                </div>
                            );
                        }

                        if ('min' in param) {
                            return (
                                <div className="param-row">
                                    <label>{param.name}:</label>
                                    <input
                                        onChange={(e) => {
                                            changeParam(index, 'min', e.currentTarget.value);
                                            correctInputType(e, param.type);
                                        }}
                                        value={param.min}
                                        type="number"
                                        step={param.type == 'float' ? 0.1 : 1}
                                        min={0}
                                        disabled={isStarted}
                                    />
                                    <span className="separator">-</span>
                                    <input
                                        onInput={(e) => correctInputType(e, param.type)}
                                        onChange={(e) => changeParam(index, 'max', e.currentTarget.value)}
                                        value={param.max}
                                        type="number"
                                        step={param.type == 'float' ? 0.1 : 1}
                                        min={0}
                                        disabled={isStarted}
                                    />
                                </div>
                            );
                        }
                    })}
                </>
            )}
        </div>
    );
};

export default Alogrytm;
