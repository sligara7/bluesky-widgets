import { useEffect } from 'react';

export default function useSSE(url: string, onMessage: (data: any) => void) {
  useEffect(() => {
    let es: EventSource | null = null;
    try {
      es = new EventSource(url);
      es.onmessage = (ev) => {
        try {
          const data = JSON.parse(ev.data);
          onMessage(data);
        } catch (e) {
          // ignore parse errors
        }
      };
      es.onerror = () => {
        // no-op; the browser will try to reconnect
      };
    } catch (e) {
      // EventSource may not be available in some environments; ignore
    }
    return () => {
      if (es) {
        es.close();
      }
    };
  }, [url, onMessage]);
}
