FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

COPY ./src /app
COPY requirements.txt /
RUN pip install  pip
RUN pip install -r /requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
