from fastapi import APIRouter, Depends

from gainz.services.jwt_auth import decode_auth_header
from gainz.web.api import auth, monitoring, thread

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(auth.router)
api_router.include_router(thread.router, dependencies=[Depends(decode_auth_header)])
