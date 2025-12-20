import "./ConnectionIndicator.scss";

interface Props {
  status: "CONNECTING" | "OPEN" | "CLOSED";
}

const ConnectionIndicator = ({ status }: Props) => {
  const statusConfig = {
    CONNECTING: {
      modifier: 'connecting',
      text: 'Łączenie...',
      icon: (
        <svg className="connection-indicator__icon connection-indicator__icon--spin" viewBox="0 0 24 24" fill="none">
          <circle className="connection-indicator__icon-bg" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="connection-indicator__icon-path" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
        </svg>
      )
    },
    OPEN: {
      modifier: 'open',
      text: 'Połączono',
      icon: (
        <svg className="connection-indicator__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <polyline points="20 6 9 17 4 12" />
        </svg>
      )
    },
    CLOSED: {
      modifier: 'closed',
      text: 'Rozłączono',
      icon: (
        <svg className="connection-indicator__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <line x1="18" y1="6" x2="6" y2="18" />
          <line x1="6" y1="6" x2="18" y2="18" />
        </svg>
      )
    }
  };

  const config = statusConfig[status];

  return (
    <div className="connection-indicator">
      <div className="connection-indicator__card">
        <div className={`connection-indicator__badge connection-indicator__badge--${config.modifier}`}>
          {config.icon}
        </div>
        <div className="connection-indicator__info">
          <span className="connection-indicator__label">serwer</span>
          <span className="connection-indicator__status-text">{config.text}</span>
        </div>
      </div>
    </div>
  );
};

export default ConnectionIndicator;