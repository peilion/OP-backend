import os

API_V1_STR = "/api/v1"
SECRET_KEY = os.urandom(32)
DATABASE_CONNECTION_URL = os.getenv("DATABASE_CONNECTION_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME")
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 8  # 60 minutes * 24 hours * 8 days = 8 days

SERVER_NAME = os.getenv("SERVER_NAME")
SERVER_HOST = os.getenv("SERVER_HOST")


BACKEND_CORS_ORIGINS = "http://localhost:9527,http://123.56.7.137"  # a string of origins separated by commas, e.g: "http://localhost, http://localhost:4200, http://localhost:3000, http://localhost:8080, http://local.dockertoolbox.tiangolo.com"
PROJECT_NAME = "Oil Pump Data Api"

TIME_DOMAIN_SUB_SAMPLED_RATIO = 4
TIME_DOMAIN_DECIMAL = 3
