import './Raport.scss';

interface Props {
    result: any;
}

const Raport = ({ result }: Props) => {
    return (
        <div>
            Result:
            <pre className="algorithm-card">{JSON.stringify(result.result, null, 2)}</pre>
            Figures:
            <pre className="algorithm-card">{JSON.stringify(result.figures, null, 2)}</pre>
        </div>
    );
};

export default Raport;
