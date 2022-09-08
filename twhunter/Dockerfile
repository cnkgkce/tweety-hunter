FROM python:3.9.5-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /usr/src/app
RUN pip install --upgrade pip
RUN pip install psycopg2-binary
COPY requirements.txt ./
RUN pip install -r requirements.txt 