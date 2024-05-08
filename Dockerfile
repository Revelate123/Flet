# syntax=docker/dockerfile:1

FROM python:3.11.9-slim

WORKDIR /app
ENV FLASK_APP=main.py
ENV FLASK_RUN_HOST=0.0.0.0

COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir --upgrade -r requirements.txt 
EXPOSE 5000
COPY . .

CMD ["gunicorn", "--bind","0.0.0.0:5000", "app:app"]