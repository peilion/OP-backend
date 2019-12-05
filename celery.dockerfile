FROM python:3.7

COPY ./src /app
COPY requirements.txt /
COPY ./src/worker-start.sh /worker-start.sh

RUN pip install -r /requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

WORKDIR /app

ENV PYTHONPATH=/app

RUN chmod +x /worker-start.sh

CMD ["bash", "/worker-start.sh"]
