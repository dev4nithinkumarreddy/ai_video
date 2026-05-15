import logging
from typing import Dict, List, Any, Optional
from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections and broadcasts progress updates"""
    
    def __init__(self):
        # Store active connections by client ID
        self.active_connections: Dict[str, WebSocket] = {}
        # Store subscriptions by job ID
        self.job_subscriptions: Dict[str, List[str]] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Connect a new WebSocket client"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"WebSocket client connected: {client_id}")
    
    def disconnect(self, client_id: str):
        """Disconnect a WebSocket client"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"WebSocket client disconnected: {client_id}")
        
        # Remove from all subscriptions
        for job_id, subscribers in self.job_subscriptions.items():
            if client_id in subscribers:
                subscribers.remove(client_id)
    
    async def subscribe_to_job(self, client_id: str, job_id: str):
        """Subscribe a client to job progress updates"""
        if job_id not in self.job_subscriptions:
            self.job_subscriptions[job_id] = []
        
        if client_id not in self.job_subscriptions[job_id]:
            self.job_subscriptions[job_id].append(client_id)
            logger.info(f"Client {client_id} subscribed to job {job_id}")
    
    async def unsubscribe_from_job(self, client_id: str, job_id: str):
        """Unsubscribe a client from job progress updates"""
        if job_id in self.job_subscriptions and client_id in self.job_subscriptions[job_id]:
            self.job_subscriptions[job_id].remove(client_id)
            logger.info(f"Client {client_id} unsubscribed from job {job_id}")
    
    async def send_personal_message(self, client_id: str, message: Dict[str, Any]):
        """Send a message to a specific client"""
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending message to client {client_id}: {str(e)}")
                self.disconnect(client_id)
    
    async def broadcast_to_job(self, job_id: str, message: Dict[str, Any]):
        """Broadcast a message to all clients subscribed to a job"""
        if job_id in self.job_subscriptions:
            disconnected_clients = []
            
            for client_id in self.job_subscriptions[job_id]:
                if client_id in self.active_connections:
                    websocket = self.active_connections[client_id]
                    try:
                        await websocket.send_text(json.dumps(message))
                    except Exception as e:
                        logger.error(f"Error broadcasting to client {client_id}: {str(e)}")
                        disconnected_clients.append(client_id)
                else:
                    disconnected_clients.append(client_id)
            
            # Remove disconnected clients
            for client_id in disconnected_clients:
                self.disconnect(client_id)
    
    async def broadcast_to_all(self, message: Dict[str, Any]):
        """Broadcast a message to all connected clients"""
        disconnected_clients = []
        
        for client_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error broadcasting to client {client_id}: {str(e)}")
                disconnected_clients.append(client_id)
        
        # Remove disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)
    
    def get_connection_count(self) -> int:
        """Get the number of active connections"""
        return len(self.active_connections)
    
    def get_job_subscriber_count(self, job_id: str) -> int:
        """Get the number of subscribers for a job"""
        return len(self.job_subscriptions.get(job_id, []))


# Global WebSocket manager instance
websocket_manager = WebSocketManager()


class ProgressBroadcaster:
    """Service for broadcasting progress updates via WebSocket"""
    
    def __init__(self, manager: WebSocketManager):
        self.manager = manager
    
    async def broadcast_script_progress(self, job_id: str, progress_data: Dict[str, Any]):
        """Broadcast script generation progress"""
        message = {
            "type": "script_progress",
            "job_id": job_id,
            "timestamp": datetime.utcnow().isoformat(),
            "data": progress_data
        }
        await self.manager.broadcast_to_job(job_id, message)
    
    async def broadcast_audio_progress(self, job_id: str, progress_data: Dict[str, Any]):
        """Broadcast audio generation progress"""
        message = {
            "type": "audio_progress",
            "job_id": job_id,
            "timestamp": datetime.utcnow().isoformat(),
            "data": progress_data
        }
        await self.manager.broadcast_to_job(job_id, message)
    
    async def broadcast_image_progress(self, job_id: str, progress_data: Dict[str, Any]):
        """Broadcast image generation progress"""
        message = {
            "type": "image_progress",
            "job_id": job_id,
            "timestamp": datetime.utcnow().isoformat(),
            "data": progress_data
        }
        await self.manager.broadcast_to_job(job_id, message)
    
    async def broadcast_video_progress(self, job_id: str, progress_data: Dict[str, Any]):
        """Broadcast video rendering progress"""
        message = {
            "type": "video_progress",
            "job_id": job_id,
            "timestamp": datetime.utcnow().isoformat(),
            "data": progress_data
        }
        await self.manager.broadcast_to_job(job_id, message)
    
    async def broadcast_job_completed(self, job_id: str, result_data: Dict[str, Any]):
        """Broadcast job completion notification"""
        message = {
            "type": "job_completed",
            "job_id": job_id,
            "timestamp": datetime.utcnow().isoformat(),
            "data": result_data
        }
        await self.manager.broadcast_to_job(job_id, message)
    
    async def broadcast_job_failed(self, job_id: str, error_data: Dict[str, Any]):
        """Broadcast job failure notification"""
        message = {
            "type": "job_failed",
            "job_id": job_id,
            "timestamp": datetime.utcnow().isoformat(),
            "data": error_data
        }
        await self.manager.broadcast_to_job(job_id, message)
    
    async def broadcast_system_status(self, status_data: Dict[str, Any]):
        """Broadcast system status updates"""
        message = {
            "type": "system_status",
            "timestamp": datetime.utcnow().isoformat(),
            "data": status_data
        }
        await self.manager.broadcast_to_all(message)


# Global progress broadcaster instance
progress_broadcaster = ProgressBroadcaster(websocket_manager)


def get_websocket_manager() -> WebSocketManager:
    """Get the WebSocket manager instance"""
    return websocket_manager


def get_progress_broadcaster() -> ProgressBroadcaster:
    """Get the progress broadcaster instance"""
    return progress_broadcaster
