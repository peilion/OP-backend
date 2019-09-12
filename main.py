from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
import uvicorn
from core import config
from api.api_v1.api import api_router

app = FastAPI(title=config.PROJECT_NAME, openapi_url="/api/v1/openapi.json")

# CORS
origins = []

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


app.include_router(api_router, prefix=config.API_V1_STR)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info", reload=True, debug=True)
