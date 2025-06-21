from fastapi import WebSocket
from typing import Dict, List
import json
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.score_connections: List[WebSocket] = []
        self.leaderboard_connections: List[WebSocket] = []
    
    async def connect_score_updates(self, websocket: WebSocket):
        await websocket.accept()
        self.score_connections.append(websocket)
        logger.info(f"Score updates connection established. Total: {len(self.score_connections)}")
    
    async def connect_leaderboard(self, websocket: WebSocket):
        await websocket.accept()
        self.leaderboard_connections.append(websocket)
        logger.info(f"Leaderboard connection established. Total: {len(self.leaderboard_connections)}")
    
    def disconnect_score_updates(self, websocket: WebSocket):
        if websocket in self.score_connections:
            self.score_connections.remove(websocket)
            logger.info(f"Score updates connection removed. Total: {len(self.score_connections)}")
    
    def disconnect_leaderboard(self, websocket: WebSocket):
        if websocket in self.leaderboard_connections:
            self.leaderboard_connections.remove(websocket)
            logger.info(f"Leaderboard connection removed. Total: {len(self.leaderboard_connections)}")
    
    async def broadcast_score_update(self, data: dict):
        """Broadcast score changes to all connected clients"""
        if not self.score_connections:
            return
        
        message = json.dumps(data)
        disconnected = []
        
        for connection in self.score_connections:
            try:
                await connection.send_text(message)
            except Exception:
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect_score_updates(conn)
    
    async def broadcast_leaderboard_update(self, leaderboard_data: list):
        """Broadcast top 5 leaderboard to all connected clients"""
        if not self.leaderboard_connections:
            return
        
        message = json.dumps({"top5": leaderboard_data})
        disconnected = []
        
        for connection in self.leaderboard_connections:
            try:
                await connection.send_text(message)
            except Exception:
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect_leaderboard(conn)

# Global connection manager instance
manager = ConnectionManager()