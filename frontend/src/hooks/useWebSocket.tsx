import { useState, useEffect, useCallback, useRef } from 'react';

export type ReadyState = 'CONNECTING' | 'OPEN' | 'CLOSED';

interface WebSocketOptions {
    maxRetries?: number;
    initialDelay?: number;
    autoConnect?: boolean;
}

interface Message {
    type: string;
    message: any;
}

/**
 * Hook useWebSocket z obsługą TypeScript, Reconnection i Typowaniem Wiadomości
 * @template T Typ danych przychodzących z serwera
 */
const useWebSocket = (url: string, options: WebSocketOptions = {}) => {
    const { maxRetries = 5, initialDelay = 1000, autoConnect = true } = options;

    const [lastMessage, setLastMessage] = useState<Message | null>(null);
    const [readyState, setReadyState] = useState<ReadyState>('CONNECTING');
    const [currentRetryCount, setCurrentRetryCount] = useState(0);

    const ws = useRef<WebSocket | null>(null);
    const retryCountRef = useRef(0);
    const reconnectionTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

    const connect = useCallback(() => {
        // Zapobiegamy tworzeniu wielu połączeń jednocześnie
        if (ws.current?.readyState === WebSocket.OPEN) return;

        const socket = new WebSocket(url);
        ws.current = socket;
        setReadyState('CONNECTING');

        socket.onopen = () => {
            setReadyState('OPEN');
            retryCountRef.current = 0;
            setCurrentRetryCount(0);
        };

        socket.onmessage = (event: MessageEvent) => {
            try {
                const data = JSON.parse(event.data) as Message;
                setLastMessage(data);
            } catch (e) {
                setLastMessage(event.data as unknown as Message);
            }
        };

        socket.onclose = (event: CloseEvent) => {
            setReadyState('CLOSED');

            // Logika reconnektu tylko jeśli zamknięcie nie było celowe
            if (!event.wasClean && retryCountRef.current < maxRetries) {
                const delay = initialDelay * Math.pow(2, retryCountRef.current);

                reconnectionTimer.current = setTimeout(() => {
                    retryCountRef.current += 1;
                    setCurrentRetryCount(retryCountRef.current);
                    connect();
                }, delay);
            }
        };

        socket.onerror = () => {
            // Wywołanie close() uruchomi logikę onclose z reconnectem
            socket.close();
        };
    }, [url, maxRetries, initialDelay]);

    useEffect(() => {
        if (autoConnect) {
            connect();
        }

        return () => {
            if (reconnectionTimer.current) clearTimeout(reconnectionTimer.current);
            if (ws.current) ws.current.close(1000, 'Component unmounted');
        };
    }, [connect, autoConnect]);

    const sendMessage = useCallback((data: any) => {
        if (ws.current?.readyState === WebSocket.OPEN) {
            const message = typeof data === 'string' ? data : JSON.stringify(data);
            ws.current.send(message);
        }
    }, []);

    return {
        lastMessage,
        sendMessage,
        readyState,
        retryCount: currentRetryCount,
        connect,
    };
};

export default useWebSocket;
