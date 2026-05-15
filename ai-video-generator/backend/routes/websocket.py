import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Optional

from services.websocket_service import get_websocket_manager, get_progress_broadcaster

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """
    WebSocket endpoint for real-time progress updates
    
    Args:
        websocket: WebSocket connection
        client_id: Unique client identifier
    """
    manager = get_websocket_manager()
    
    try:
        await manager.connect(websocket, client_id)
        
        # Send welcome message
        await manager.send_personal_message(client_id, {
            "type": "connection_established",
            "client_id": client_id,
            "message": "Connected to progress updates"
        })
        
        # Keep connection alive and handle messages
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_text()
                message = eval(data)  # Parse JSON message
                
                # Handle different message types
                if message.get("type") == "subscribe":
                    job_id = message.get("job_id")
                    if job_id:
                        await manager.subscribe_to_job(client_id, job_id)
                        await manager.send_personal_message(client_id, {
                            "type": "subscription_confirmed",
                            "job_id": job_id,
                            "message": f"Subscribed to job {job_id}"
                        })
                
                elif message.get("type") == "unsubscribe":
                    job_id = message.get("job_id")
                    if job_id:
                        await manager.unsubscribe_from_job(client_id, job_id)
                        await manager.send_personal_message(client_id, {
                            "type": "unsubscription_confirmed",
                            "job_id": job_id,
                            "message": f"Unsubscribed from job {job_id}"
                        })
                
                elif message.get("type") == "ping":
                    await manager.send_personal_message(client_id, {
                        "type": "pong",
                        "timestamp": message.get("timestamp")
                    })
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error handling WebSocket message from {client_id}: {str(e)}")
                break
    
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        logger.info(f"WebSocket disconnected: {client_id}")
    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {str(e)}")
        manager.disconnect(client_id)


@router.websocket("/ws/job/{job_id}")
async def websocket_job_endpoint(websocket: WebSocket, job_id: str):
    """
    WebSocket endpoint for specific job progress updates
    
    Args:
        websocket: WebSocket connection
        job_id: Job ID to subscribe to
    """
    manager = get_websocket_manager()
    
    try:
        # Generate unique client ID for this connection
        import uuid
        client_id = f"job_{job_id}_{uuid.uuid4()}"
        
        await manager.connect(websocket, client_id)
        await manager.subscribe_to_job(client_id, job_id)
        
        # Send welcome message
        await manager.send_personal_message(client_id, {
            "type": "job_connection_established",
            "client_id": client_id,
            "job_id": job_id,
            "message": f"Connected to job {job_id} updates"
        })
        
        # Keep connection alive
        while True:
            try:
                # Receive ping messages to keep connection alive
                await websocket.receive_text()
                
                # Send pong response
                await manager.send_personal_message(client_id, {
                    "type": "pong",
                    "job_id": job_id
                })
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error in job WebSocket for {client_id}: {str(e)}")
                break
    
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        logger.info(f"Job WebSocket disconnected: {client_id}")
    except Exception as e:
        logger.error(f"Job WebSocket error for {client_id}: {str(e)}")
        manager.disconnect(client_id)


@router.get("/ws/status")
async def websocket_status():
    """
    Get WebSocket connection status
    
    Returns:
        WebSocket connection statistics
    """
    manager = get_websocket_manager()
    
    return {
        "active_connections": manager.get_connection_count(),
        "job_subscriptions": {
            job_id: manager.get_job_subscriber_count(job_id)
            for job_id in manager.job_subscriptions.keys()
        }
    }


# Helper functions to broadcast progress from other services
async def broadcast_script_progress(job_id: str, progress_data: dict):
    """Helper function to broadcast script progress"""
    broadcaster = get_progress_broadcaster()
    await broadcaster.broadcast_script_progress(job_id, progress_data)


async def broadcast_audio_progress(job_id: str, progress_data: dict):
    """Helper function to broadcast audio progress"""
    broadcaster = get_progress_broadcaster()
    await broadcaster.broadcast_audio_progress(job_id, progress_data)


async def broadcast_image_progress(job_id: str, progress_data: dict):
    """Helper function to broadcast image progress"""
    broadcaster = get_progress_broadcaster()
    await broadcaster.broadcast_image_progress(job_id, progress_data)


async def broadcast_video_progress(job_id: str, progress_data: dict):
    """Helper function to broadcast video progress"""
    broadcaster = get_progress_broadcaster()
    await broadcaster.broadcast_video_progress(job_id, progress_data)
