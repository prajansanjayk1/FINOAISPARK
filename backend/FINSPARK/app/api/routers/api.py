from fastapi import APIRouter
from app.api.v1 import auth, users, assets, requests, approvals, risk, audit, dashboard, websocket

api_router = APIRouter()

# Register routes under /api/v1
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(assets.router)
api_router.include_router(requests.router)
api_router.include_router(approvals.router)
api_router.include_router(risk.router)
api_router.include_router(audit.router)
api_router.include_router(dashboard.router)
api_router.include_router(websocket.router)
