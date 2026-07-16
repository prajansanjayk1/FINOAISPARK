import json
from typing import Dict, List
from fastapi import WebSocket
from app.core.logging import logger


class WebSocketManager:
    """
    Manages active WebSocket connections for real-time compliance broadcasting,
    dashboard telemetry, and security threat alerts.
    """

    def __init__(self):
        # Maps channel name (e.g. "audit_stream", "threat_alerts") to active socket list
        self.active_channels: Dict[str, List[WebSocket]] = {
            "audit_stream": [],
            "approvals": [],
            "threat_alerts": [],
            "dashboard": []
        }

    async def connect(self, websocket: WebSocket, channel: str) -> None:
        """
        Accepts and registers a client connection under the specified channel.
        """
        await websocket.accept()
        if channel not in self.active_channels:
            self.active_channels[channel] = []
        self.active_channels[channel].append(websocket)
        logger.info(f"WebSocket client connected to channel: '{channel}'. Total channel listeners: {len(self.active_channels[channel])}")

    def disconnect(self, websocket: WebSocket, channel: str) -> None:
        """
        Removes a disconnected client from the channel list.
        """
        if channel in self.active_channels and websocket in self.active_channels[channel]:
            self.active_channels[channel].remove(websocket)
            logger.info(f"WebSocket client disconnected from channel: '{channel}'. Remaining listeners: {len(self.active_channels[channel])}")

    async def broadcast_to_channel(self, channel: str, message: dict) -> None:
        """
        Sends a JSON payload to all active listeners on a specific channel.
        """
        if channel not in self.active_channels or not self.active_channels[channel]:
            return

        dead_connections: List[WebSocket] = []
        payload_str = json.dumps(message)

        for connection in self.active_channels[channel]:
            try:
                await connection.send_text(payload_str)
            except Exception as e:
                logger.warning(f"Failed to transmit websocket message on channel '{channel}': {str(e)}. Flagging client for removal.")
                dead_connections.append(connection)

        # Cleanup connections that failed to receive broadcast
        for dead_conn in dead_connections:
            self.disconnect(dead_conn, channel)


# Global WebSocket manager instance
ws_manager = WebSocketManager()
