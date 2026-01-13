import type { AlgorithmData } from '../../interfaces';
import './Algorytm.scss';

interface Props {
    algorithmData: AlgorithmData;
    setAlgorithmData: (a: AlgorithmData[]) => void;
    algIndex: number;
    isStarted: boolean;
}

const Alogrytm = ({ algorithmData, setAlgorithmData, algIndex, isStarted }: Props) => {
    const changeParam = (paramIndex: number, type: 'min' | 'max' | 'value', value: string, paramType: 'int' | 'float') => {
        // @ts-ignore
        setAlgorithmData((algsParams) => {
            const algsParamsCopy = JSON.parse(JSON.stringify(algsParams));
            // For float: keep raw string to allow typing dots, convert to number only for int
            // Number conversion for floats happens when data is sent to server
            if (paramType === 'int') {
                algsParamsCopy[algIndex].params[paramIndex][type] = Number(value) || 0;
            } else {
                // Keep as string while typing, but also store numeric value if valid
                const numVal = parseFloat(value);
                algsParamsCopy[algIndex].params[paramIndex][type] = isNaN(numVal) ? value : numVal;
                // Store raw string for display
                algsParamsCopy[algIndex].params[paramIndex][type + '_raw'] = value;
            }
            return algsParamsCopy;
        });
    };

    // Get display value - use raw string if available, otherwise the number
    const getDisplayValue = (param: any, field: 'min' | 'max' | 'value') => {
        const rawKey = field + '_raw';
        if (rawKey in param && param[rawKey] !== undefined) {
            return param[rawKey];
        }
        return param[field];
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
                                        onChange={(e) => changeParam(index, 'value', e.currentTarget.value, param.type)}
                                        value={getDisplayValue(param, 'value')}
                                        type={param.type == 'float' ? 'text' : 'number'}
                                        inputMode={param.type == 'float' ? 'decimal' : 'numeric'}
                                        min={0}
                                        step={param.type == 'float' ? 'any' : 1}
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
                                        onChange={(e) => changeParam(index, 'min', e.currentTarget.value, param.type)}
                                        value={getDisplayValue(param, 'min')}
                                        type={param.type == 'float' ? 'text' : 'number'}
                                        inputMode={param.type == 'float' ? 'decimal' : 'numeric'}
                                        min={0}
                                        disabled={isStarted}
                                    />
                                    <span className="separator">-</span>
                                    <input
                                        onChange={(e) => changeParam(index, 'max', e.currentTarget.value, param.type)}
                                        value={getDisplayValue(param, 'max')}
                                        type={param.type == 'float' ? 'text' : 'number'}
                                        inputMode={param.type == 'float' ? 'decimal' : 'numeric'}
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
