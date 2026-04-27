from .auth import router as auth_router
from .analyze import router as analyze_router
from .cases import router as cases_router
from .dashboard import router as dashboard_router
from .admin import router as admin_router
from .websocket import router as websocket_router

__all__ = [
    "auth_router", "analyze_router", "cases_router", 
    "dashboard_router", "admin_router", "websocket_router"
]
