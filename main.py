import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api.api_v1.api import api_router
from core import config
from core.dependencies import get_mp_mapper

app = FastAPI(title=config.PROJECT_NAME, openapi_url="/api/v1/openapi.json")

# CORS
origins = ["*"]

# Set all CORS enabled origins
if config.BACKEND_CORS_ORIGINS:
    origins_raw = config.BACKEND_CORS_ORIGINS.split(",")
    for origin in origins_raw:
        use_origin = origin.strip()
        origins.append(use_origin)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@app.on_event("startup")
async def startup_event():
    get_mp_mapper()


app.include_router(api_router, prefix=config.API_V1_STR)

if __name__ == "__main__":
    uvicorn.run('main:app', host="0.0.0.0", port=8000, log_level="info", reload=True, debug=True)
