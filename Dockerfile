# syntax=docker/dockerfile:1

FROM python:3.11.9-slim

WORKDIR /python-docker
ENV FLASK_APP=main.py
ENV FLASK_RUN_HOST=0.0.0.0


COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt --no-cache-dir
EXPOSE 5000
COPY . .

CMD ["flask","run","--debug"]