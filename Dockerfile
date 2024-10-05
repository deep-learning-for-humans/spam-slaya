FROM python:3.12-alpine
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt