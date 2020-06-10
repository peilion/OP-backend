from fastapi import APIRouter

from api.api_v1.endpoints import (
    users,
    assets,
    asset_stat,
    stations,
    constant,
    warning,
    server,
    vib_data,
    measure_points,
    elec_data,
    vib_feature,
    elec_feature,
    maintenance_record,
    pipeline,
    union,
    organizations,
    assets_mset,
    threshold,
)

api_router = APIRouter()

api_router.include_router(constant.router, prefix="/const", tags=["Constants"])

api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(asset_stat.router, prefix="/assets", tags=["Assets"])
api_router.include_router(assets.router, prefix="/assets", tags=["Assets"])

api_router.include_router(stations.router, prefix="/stations", tags=["Stations"])
api_router.include_router(
    organizations.router, prefix="/organizations", tags=["Organizations"]
)
api_router.include_router(pipeline.router, prefix="/pipelines", tags=["Pipelines"])

api_router.include_router(warning.router, prefix="/warning", tags=["Warning"])
api_router.include_router(union.router, prefix="/union", tags=["Union"])
api_router.include_router(server.router, prefix="/server", tags=["Server"])
api_router.include_router(vib_data.router, tags=["Vibration"])
api_router.include_router(vib_feature.router, tags=["Vibration"])
api_router.include_router(elec_data.router, tags=["Electric"])
api_router.include_router(elec_feature.router, tags=["Electric"])
api_router.include_router(measure_points.router, prefix="/mp", tags=["Measure Points"])
api_router.include_router(
    maintenance_record.router, prefix="/maintre", tags=["Maintenance Record"]
)
api_router.include_router(assets_mset.router, tags=["MSET"], prefix="/asset")
api_router.include_router(
    threshold.router, tags=["Diagnosis Threshold"], prefix="/threshold"
)
