import type { ParamTypes } from '../../interfaces';

interface Props {
    sharedAlgsParams: ParamTypes[];
    setSharedAlgsParams: React.Dispatch<React.SetStateAction<ParamTypes[]>>;
    isStarted: boolean;
}

export function SharedParamsSection({ sharedAlgsParams, setSharedAlgsParams, isStarted }: Props) {
    const changeParam = (paramIndex: number, type: 'min' | 'max' | 'value', value: string) => {
        // @ts-ignore

        setSharedAlgsParams((params) => {
            const sharedAlgsParamsCopy = JSON.parse(JSON.stringify(params));
            sharedAlgsParamsCopy[paramIndex][type] = Number(value);
            return sharedAlgsParamsCopy;
        });
    };

    const correctInputType = (e: any, type: 'int' | 'float') => {
        if (type === 'int') {
            e.currentTarget.value = e.currentTarget.value.replace(/[^0-9]/g, '');
        } else if (type === 'float') {
            e.currentTarget.value = e.currentTarget.value.replace(/[^0-9.]/g, '');
        }
    };

    return (
        <>
            <h2>Wpólne parametry:</h2>
            <div className="algorithm-card">
                <div className="param-labels">
                    <div className="label-space"></div>
                    <div className="label-text">Wartość</div>
                </div>

                {sharedAlgsParams.map((param, index) => {
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
                    } else {
                        return (
                            <div className="param-row">
                                <label>{param.name}:</label>
                                <input
                                    onInput={(e) => correctInputType(e, param.type)}
                                    onChange={(e) => changeParam(index, 'min', e.currentTarget.value)}
                                    value={param.min}
                                    type="number"
                                    step={1}
                                    min={0}
                                    disabled={isStarted}
                                />
                                <span className="separator">-</span>
                                <input
                                    onInput={(e) => correctInputType(e, param.type)}
                                    onChange={(e) => changeParam(index, 'max', e.currentTarget.value)}
                                    value={param.max}
                                    type="number"
                                    step={1}
                                    min={0}
                                    disabled={isStarted}
                                />
                            </div>
                        );
                    }
                })}
            </div>
        </>
    );
}
