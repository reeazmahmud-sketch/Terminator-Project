import { useState, useEffect } from 'react';

/**
 * Custom hook for agent performance metrics
 * Subscribes to WebSocket metrics_update messages
 *
 * @param {WebSocket} websocket - Active WebSocket connection
 * @returns {{ agents: Array, system: Object, timestamp: string }}
 */
export const useMetrics = (websocket) => {
  const [metrics, setMetrics] = useState({
    agents: [],
    system: {
      total_agents: 0,
      agents_online: 0,
      total_messages: 0,
      total_queue_size: 0
    },
    timestamp: null
  });

  useEffect(() => {
    if (!websocket) return;

    const handleMessage = (event) => {
      try {
        const message = JSON.parse(event.data);

        // Only handle metrics updates
        if (message.type === 'metrics_update') {
          setMetrics(message.content);
        }
      } catch (err) {
        console.error('Metrics parse error:', err);
      }
    };

    websocket.addEventListener('message', handleMessage);

    return () => {
      websocket.removeEventListener('message', handleMessage);
    };
  }, [websocket]);

  return metrics;
};
