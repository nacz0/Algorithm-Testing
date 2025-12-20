import  { useState, useEffect, useCallback } from 'preact/hooks';
import './NotificationManager.scss';

interface ToastItem {
  id: string | number;
  message: string;
  color: string;
}

interface NotificationManagerProps {
  newMessage: string;
  color?: string;
  id: string | number | null;
}

const NotificationManager = ({ newMessage, color, id }: NotificationManagerProps) => {
  const [toasts, setToasts] = useState<ToastItem[]>([]);

  const removeToast = useCallback((idToHide: string | number) => {
    setToasts((prev) => prev.filter((t) => t.id !== idToHide));
  }, []);

  useEffect(() => {
    if (id && newMessage) {
      const newToast: ToastItem = {
        id: id,
        message: newMessage,
        color: color || '#333'
      };

      setToasts((prev) => [...prev, newToast]);

      setTimeout(() => {
        removeToast(id);
      }, 5000);
    }
    // Usunęliśmy return z clearTimeout, bo chcemy, 

  }, [id, newMessage, color, removeToast]);

  return (
    <div className="toast-container">
      {toasts.map((t) => (
        <div 
          key={t.id} 
          className="toast-item" 
          style={{ backgroundColor: t.color }}
        >
          <span>{t.message}</span>
          <button onClick={() => removeToast(t.id)} className="close-btn">
            &times;
          </button>
        </div>
      ))}
    </div>
  );
};

export default NotificationManager;