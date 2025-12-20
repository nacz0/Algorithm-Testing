import type { AlgorithmData } from '../../interfaces';
import './Algorytm.scss';

interface Props {
    algorithmData: AlgorithmData;
    setAlgorithmData: (a: AlgorithmData[]) => void;
    algIndex: number;
}

const Alogrytm = ({ algorithmData, setAlgorithmData, algIndex }: Props) => {
    const changeParam = (paramIndex: number, type: 'min' | 'max' | 'step' | 'value', value: string) => {
        // @ts-ignore
        setAlgorithmData((algsParams) => {
            const algsParamsCopy = JSON.parse(JSON.stringify(algsParams));
            algsParamsCopy[algIndex].args[paramIndex][type] = Number(value);
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
                <h3>{algorithmData.name}</h3>
                <div onClick={() => toggleState()} className={`toggle-switch ${algorithmData.isUsed && 'active'}`} data-algo="bat">
                    <div className="toggle-slider"></div>
                </div>
            </div>

            {algorithmData.args.length == 0 ? (
                "Brak argumentów"
                
            ) : (
                <>
                    <div className="param-labels">
                        <div className="label-space"></div>
                        <div className="label-text">Min</div>
                        <div className="separator"></div>
                        <div className="label-text">Max</div>
                        <div className="separator"></div>
                        <div className="label-text">Step</div>
                    </div>

                    {/* Wiersze parametrów (przykłady) */}

                    {algorithmData.args.map((arg, index) => {
                        if ('value' in arg) {
                            return (
                                <div className="param-row">
                                    <label>{arg.name}:</label>
                                    <input onChange={(e) => changeParam(index, 'value', e.currentTarget.value)} value={arg.value} type="number" min={0} />
                                </div>
                            );
                        }

                        if ('step' in arg) {
                            return (
                                <div className="param-row">
                                    <label>{arg.name}:</label>
                                    <input onChange={(e) => changeParam(index, 'min', e.currentTarget.value)} value={arg.min} type="number" step={1} min={0} />
                                    <span className="separator">-</span>
                                    <input onChange={(e) => changeParam(index, 'max', e.currentTarget.value)} value={arg.max} type="number" step={1} min={0} />
                                    <span className="separator">,</span>
                                    <input onChange={(e) => changeParam(index, 'step', e.currentTarget.value)} value={arg.step} type="number" step={1} min={0} />
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
