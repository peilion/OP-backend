from fastapi import APIRouter
from api.api_v1.endpoints import users, assets, stations,constant,warning,server,vib_signal

api_router = APIRouter()

api_router.include_router(constant.router, prefix='/const', tags=["Constants"])

api_router.include_router(users.router, prefix='/users', tags=["Users"])
api_router.include_router(assets.router, prefix='/assets', tags=["Assets"])
api_router.include_router(stations.router, prefix='/stations', tags=["Stations"])
api_router.include_router(warning.router, prefix='/warning', tags=["Warning"])
api_router.include_router(server.router,prefix='/server',tags=['Server'])
api_router.include_router(vib_signal.router,prefix='/vib',tags=['Vibration'])