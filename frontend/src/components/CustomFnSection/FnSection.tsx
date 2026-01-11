import { useRef, useState } from 'preact/hooks';
import './FnSection.scss';
import type { FnData } from '../../interfaces.ts';

interface Props {
    fnsData: FnData[];
    setFn: (arg: FnData) => void;
    selectedFn: FnData;
    isStarted: boolean;
}

const CustomFnSection = ({ fnsData, setFn, selectedFn, isStarted }: Props) => {
    const customFnInputContainer = useRef<HTMLDivElement>(null);
    const textAreaEl = useRef<HTMLTextAreaElement>(null);
    const lowerRangeEl = useRef<HTMLInputElement>(null);
    const upperRangeEl = useRef<HTMLInputElement>(null);
    const [isCustomInputShow, setIsCustomInputShow] = useState(false);

    const setFnFromInput = () => {
        if (!textAreaEl.current) {
            return;
        }

        const regexPython = /^\s*def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(/gm;
        const code = textAreaEl.current.value;
        const matches = [...code.matchAll(regexPython)];

        const fnName = matches[0][1];

        const lowerRange = lowerRangeEl.current?.value ? parseFloat(lowerRangeEl.current.value) : -10;
        const upperRange = upperRangeEl.current?.value ? parseFloat(upperRangeEl.current.value) : 10;

        setIsCustomInputShow(false);
        setFn({ name: fnName, code: code, isCustom: true, bounds: [lowerRange, upperRange] });
        console.log({ name: fnName, code: code, isCustom: true, bounds: [lowerRange, upperRange] });
    };

    const setBuildInFn = (e: any) => {
        const index: number = e.currentTarget.value;
        const fnData = fnsData[index];
        setFn({ ...fnData, isCustom: false });
    };

    return (
        <>
            <div ref={customFnInputContainer} className={`CustomFn ${isCustomInputShow && 'CustomFn--show'}`}>
                <div className="CustomFn__section">
                    <h4>Wprowadź funkcję Python</h4>
                    <button onClick={() => setIsCustomInputShow(false)} className="CustomFn__cross">
                        x
                    </button>
                    <textarea ref={textAreaEl} rows={10}></textarea> <br />
                    <br />
                    <div className="CustomFn__rangeInputs">
                        <label className="CustomFn__rangeLabel">
                            Min: <input ref={lowerRangeEl} type="number" className="CustomFn__rangeInput" placeholder="Lower range" />
                        </label>
                        <label className="CustomFn__rangeLabel">
                            Max: <input ref={upperRangeEl} type="number" className="CustomFn__rangeInput" placeholder="Upper range" />
                        </label>
                    </div>
                    <br />
                    <button onClick={() => setFnFromInput()} className="CustomFn__btn-load">
                        Ładuj
                    </button>
                </div>
            </div>

            <div className="FnSection">
                <h2>Funkcje:</h2>
                <div className="FnSection__section">
                    <div className="FnSection__grid">
                        <div className="FnSection__form-group">
                            <label className={`FnSectin__sectionInfo ${selectedFn.isCustom && 'FnSection__highlight'} `} htmlFor="custom-function">
                                Własna funkcja:
                            </label>
                            <div>
                                <button onClick={() => setIsCustomInputShow(true)}>Load</button>
                                <input id="custom-function" disabled type="text" value={selectedFn.isCustom ? selectedFn.name : ''} placeholder="Nie wybrano" />
                            </div>
                        </div>
                        <div className="FnSection__form-group">
                            <label className={`FnSectin__sectionInfo ${!selectedFn.isCustom && 'FnSection__highlight'}`} htmlFor="builtin-function">
                                Wbudowane:
                            </label>
                            <select id="builtin-function" onChange={(e) => setBuildInFn(e)}>
                                {fnsData.map((fnData, index) => (
                                    <option value={index}>{fnData.name}</option>
                                ))}
                            </select>
                        </div>
                    </div>
                </div>
            </div>
        </>
    );
};

export default CustomFnSection;
