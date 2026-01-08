import './ProgressBar.scss';

interface Props {
    label: string;
    progress: number;
}

const ProgressBar = ({ label, progress }: Props) => {
    return (
        <div class="progress-item">
            <div class="progress-header">
                <span class="progress-label">{label}</span>
                <span class="progress-percentage" id="progress-bat-text">
                    {Math.round(progress)}%
                </span>
            </div>
            <div class="progress-bar-bg">
                <div style={{ width: `${progress}%` }} class="progress-bar" id="progress-bat"></div>
            </div>
        </div>
    );
};

export default ProgressBar;
