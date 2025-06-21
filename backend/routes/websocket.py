from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from websocket_manager import manager
import logging

logger = logging.getLogger(__name__)
websocket_router = APIRouter()

@websocket_router.websocket("/ws/score_updates")
async def websocket_score_updates(websocket: WebSocket):
    await manager.connect_score_updates(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect_score_updates(websocket)
        logger.info("Score updates WebSocket disconnected")

@websocket_router.websocket("/ws/leaderboard")
async def websocket_leaderboard(websocket: WebSocket):
    await manager.connect_leaderboard(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect_leaderboard(websocket)
        logger.info("Leaderboard WebSocket disconnected")