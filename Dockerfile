# syntax=docker/dockerfile:1

FROM python:3.11.9-slim

WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
EXPOSE 8080
COPY . .

CMD [ "python3", "main.py"]