# syntax=docker/dockerfile:1

FROM python:3.11.9-slim

WORKDIR /app
ENV FLASK_APP=main.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV CLIENT_SECRETS_FILE='client_secret_2_319728086235-ubuom2fs3laa07rgohgqr9m4mqe00sbc.apps.googleusercontent.com.json'
ENV FUTURE_PRODUCER='future-producer-418904-ed3008c258c5.json'

COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir --upgrade -r requirements.txt 
EXPOSE 5000
COPY . .

CMD ["gunicorn", "--bind","0.0.0.0:5000", "app:app"]