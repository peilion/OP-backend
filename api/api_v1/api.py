from fastapi import APIRouter

from api.api_v1.endpoints import  users,assets

api_router = APIRouter()
api_router.include_router(users.router, prefix='/users', tags=["login"])
api_router.include_router(assets.router, prefix='/assets', tags=["asset"])
