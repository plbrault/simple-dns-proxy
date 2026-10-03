FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY dns_server.py .
EXPOSE 53/udp
CMD ["python", "dns_server.py"]
