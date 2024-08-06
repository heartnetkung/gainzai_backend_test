from fastapi.routing import APIRouter

from gainz.web.api import auth, monitoring, thread

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(auth.router)
api_router.include_router(thread.router)
