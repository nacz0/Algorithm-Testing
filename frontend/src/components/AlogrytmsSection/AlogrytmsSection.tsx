
import "./AlgorytmsSection.scss"
import Alogrytm from './Algorytm';
import type { AlgorithmData } from "../../interfaces";


interface Props{
    algorithmData: AlgorithmData[];
    setAlgorithmData: (a: AlgorithmData[]) => void;
}

const AlogrytmsSection = ({ algorithmData, setAlgorithmData}: Props) => {
    return (
        <div>
            <h2>Algorytmy:</h2>
            <div className="AlogrytmsSection">
                {algorithmData.map((data, index) => <Alogrytm algIndex={index} algorithmData={data} setAlgorithmData={setAlgorithmData}/>)}
                
            </div>
        </div>
    );
}

export default AlogrytmsSection;