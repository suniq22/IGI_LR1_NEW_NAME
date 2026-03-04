FROM python:3.11-slim

RUN apt-get update && apt-get install -y git

WORKDIR /app

RUN git clone https://github.com/smartiqaorg/geometric_lib.git

COPY app.py .

ENV PYTHONPATH=/app

CMD ["python", "app.py"]
