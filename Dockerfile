FROM python:3.12-alpine

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt

EXPOSE 8080

#CMD [ "python", "./run.py" ]