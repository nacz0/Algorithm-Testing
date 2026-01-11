import './Raport.scss';

interface Props {
    results: any;
}

const Raport = ({ results }: Props) => {
    return (
        <div>
            {results && (
                <div className="raport-card">
                    <h2 className="raport-title">Results:</h2>

                    {Object.entries(results.result).map(([algoName, params]) => (
                        <div key={algoName} className="algorithm-section">
                            <h3 className="algorithm-title">{algoName} Algorithm</h3>

                            {/* Parameters */}
                            <div className="parameters-wrapper">
                                <h4>Parameters:</h4>
                                <div className="parameters-grid">
                                    {Object.entries(params as any).map(([key, value]) => (
                                        <div key={key} className="parameter-item">
                                            <div className="label">{key.replace(/_/g, ' ')}</div>
                                            <div className="value">{typeof value === 'number' ? value.toFixed(4) : (value as any)}</div>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {/* Figures */}
                            {results.figures[algoName] && (
                                <div className="figures-grid">
                                    {/* Convergence Plot */}
                                    {results.figures[algoName].convergence_plot && (
                                        <div className="figure-card">
                                            <h4>Convergence Plot:</h4>
                                            <img src={'data:image/png;base64,' + results.figures[algoName].convergence_plot} alt={`${algoName} Convergence Plot`} />
                                        </div>
                                    )}

                                    {/* Animation */}
                                    {results.figures[algoName].animation && (
                                        <div className="figure-card">
                                            <h4>Animation:</h4>
                                            <img src={'data:image/gif;base64,' + results.figures[algoName].animation} alt={`${algoName} Animation`} />
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default Raport;
