FROM python:3.12-slim

WORKDIR /app

COPY . .

# SQLite 数据库放到挂载卷，避免重新部署时丢失数据
ENV DATA_DIR=/data
VOLUME ["/data"]

EXPOSE 8000

CMD ["python", "server.py"]
