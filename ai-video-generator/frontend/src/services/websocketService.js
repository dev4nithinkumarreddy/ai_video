class WebSocketService {
  constructor() {
    this.ws = null;
    this.clientId = null;
    this.subscriptions = new Map();
    this.listeners = new Map();
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000;
    this.isConnecting = false;
    this.isManualDisconnect = false;
  }

  // Initialize WebSocket connection
  async connect(clientId = null) {
    if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.OPEN)) {
      return;
    }

    this.isConnecting = true;
    this.isManualDisconnect = false;
    
    try {
      // Generate client ID if not provided
      if (!clientId) {
        clientId = `client_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      }
      
      this.clientId = clientId;
      
      // Connect to WebSocket
      const wsBaseUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';
      const wsUrl = `${wsBaseUrl}/ws/ws/${clientId}`;
      this.ws = new WebSocket(wsUrl);

      // Set up event handlers
      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.isConnecting = false;
        this.reconnectAttempts = 0;
        this.reconnectDelay = 1000;
        
        // Re-subscribe to previous jobs
        this.resubscribeAll();
        
        // Notify listeners
        this.emit('connected', { clientId });
      };

      this.ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          this.handleMessage(message);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      this.ws.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason);
        this.isConnecting = false;
        
        if (!this.isManualDisconnect && this.reconnectAttempts < this.maxReconnectAttempts) {
          this.scheduleReconnect();
        } else if (this.isManualDisconnect) {
          this.emit('disconnected', { manual: true });
        } else {
          this.emit('disconnected', { manual: false, error: 'Max reconnection attempts reached' });
        }
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.emit('error', { error });
      };

    } catch (error) {
      console.error('Error connecting to WebSocket:', error);
      this.isConnecting = false;
      this.emit('error', { error });
    }
  }

  // Disconnect WebSocket
  disconnect() {
    this.isManualDisconnect = true;
    
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    
    this.subscriptions.clear();
    this.emit('disconnected', { manual: true });
  }

  // Subscribe to job progress updates
  subscribeToJob(jobId) {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.warn('WebSocket not connected, cannot subscribe to job');
      return false;
    }

    this.subscriptions.set(jobId, true);
    
    // Send subscription message
    const message = {
      type: 'subscribe',
      job_id: jobId
    };
    
    this.ws.send(JSON.stringify(message));
    console.log(`Subscribed to job: ${jobId}`);
    return true;
  }

  // Unsubscribe from job progress updates
  unsubscribeFromJob(jobId) {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      return false;
    }

    this.subscriptions.delete(jobId);
    
    // Send unsubscribe message
    const message = {
      type: 'unsubscribe',
      job_id: jobId
    };
    
    this.ws.send(JSON.stringify(message));
    console.log(`Unsubscribed from job: ${jobId}`);
    return true;
  }

  // Re-subscribe to all jobs (used after reconnection)
  resubscribeAll() {
    for (const jobId of this.subscriptions.keys()) {
      this.subscribeToJob(jobId);
    }
  }

  // Handle incoming messages
  handleMessage(message) {
    const { type, job_id, data, timestamp } = message;
    
    // Emit specific event types
    this.emit(type, { jobId: job_id, data, timestamp });
    
    // Also emit generic message event
    this.emit('message', message);
  }

  // Send ping message
  ping() {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      const message = {
        type: 'ping',
        timestamp: Date.now()
      };
      this.ws.send(JSON.stringify(message));
    }
  }

  // Schedule reconnection
  scheduleReconnect() {
    setTimeout(() => {
      this.reconnectAttempts++;
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      this.connect(this.clientId);
    }, this.reconnectDelay);
    
    // Exponential backoff
    this.reconnectDelay = Math.min(this.reconnectDelay * 2, 30000);
  }

  // Event emitter methods
  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
  }

  off(event, callback) {
    if (this.listeners.has(event)) {
      const callbacks = this.listeners.get(event);
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error('Error in event listener:', error);
        }
      });
    }
  }

  // Get connection status
  getConnectionStatus() {
    if (!this.ws) return 'disconnected';
    
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING:
        return 'connecting';
      case WebSocket.OPEN:
        return 'connected';
      case WebSocket.CLOSING:
        return 'closing';
      case WebSocket.CLOSED:
        return 'disconnected';
      default:
        return 'unknown';
    }
  }

  // Check if connected
  isConnected() {
    return this.ws && this.ws.readyState === WebSocket.OPEN;
  }
}

// Create singleton instance
const websocketService = new WebSocketService();

export default websocketService;
