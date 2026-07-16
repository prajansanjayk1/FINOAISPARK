from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
import jwt

from app.core.security import decode_token
from app.infrastructure.websocket.manager import ws_manager

router = APIRouter(tags=["Real-time Broadcaster"])


@router.websocket("/ws/{channel}")
async def websocket_endpoint(
    websocket: WebSocket,
    channel: str,
    token: str = Query(...)
):
    """
    WebSocket channel endpoint. Authorizes callers via token query query parameters.
    Channels: 'audit_stream', 'approvals', 'threat_alerts', 'dashboard'.
    """
    # 1. Channel verification
    if channel not in ws_manager.active_channels:
        await websocket.close(code=4000, reason="Invalid channel subscription request.")
        return

    # 2. Token authentication
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if not user_id:
            await websocket.close(code=4001, reason="Authentication failed: Subject missing.")
            return
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        await websocket.close(code=4003, reason="Authentication failed: Token is invalid or expired.")
        return

    # 3. Connection registration
    await ws_manager.connect(websocket, channel)
    
    try:
        # Keep the socket link open, reading incoming messages if any
        while True:
            # Clients do not publish back, but we read to detect socket dropouts
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, channel)
    except Exception:
        ws_manager.disconnect(websocket, channel)
