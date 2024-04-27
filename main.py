from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
import vertexai.generative_models
from werkzeug.security import check_password_hash, generate_password_hash
import requests
import sqlite3
from helpers import apology, login_required


import vertexai
import google.oauth2.credentials
import google_auth_oauthlib.flow
from oauth2client import tools
from google.oauth2 import service_account
from google.cloud import datastore

import os
import flask
import requests

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']
API_SERVICE_NAME = 'drive'
API_VERSION = 'v2'


app = Flask(__name__)

app.secret_key = 'REPLACE ME - this value is here as a placeholder.'

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


credentials = service_account.Credentials.from_service_account_file(
    'future-producer-418904-5b9b595c6c5e.json')

vertexai.init(credentials=credentials)


model = vertexai.generative_models.GenerativeModel("gemini-pro")





@app.route('/authorize')
def authorize():
  # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES)

  # The URI created here must exactly match one of the authorized redirect URIs
  # for the OAuth 2.0 client, which you configured in the API Console. If this
  # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
  # error.
  flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

  authorization_url, state = flow.authorization_url(
      # Enable offline access so that you can refresh an access token without
      # re-prompting the user for permission. Recommended for web server apps.
      access_type='offline',
      # Enable incremental authorization. Recommended as a best practice.
      include_granted_scopes='true')

  # Store the state so the callback can verify the auth server response.
  flask.session['state'] = state

  return flask.redirect(authorization_url)




@app.route('/oauth2callback')
def oauth2callback():
  # Specify the state when creating the flow in the callback so that it can
  # verified in the authorization server response.
  state = flask.session['state']

  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
  flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

  # Use the authorization server's response to fetch the OAuth 2.0 tokens.
  authorization_response = flask.request.url
  flow.fetch_token(authorization_response=authorization_response)

  # Store credentials in the session.
  # ACTION ITEM: In a production app, you likely want to save these
  #              credentials in a persistent database instead.
  credentials = flow.credentials
  flask.session['credentials'] = credentials_to_dict(credentials)

  return flask.redirect(flask.url_for('test_api_request'))







@app.route('/', methods=['GET', 'POST'])
@login_required
def main():
    if request.method == "POST":
        chat_request = request.form.get("chat_request")
        model_response = model.generate_content("Extract and return as text, only one location from the following sentence. Do not return any other text and do not provide a full stop.:" + chat_request).text
        #If they did not provide a location then I need a way to know
        print(model_response)
        location = requests.get("https://maps.googleapis.com/maps/api/place/findplacefromtext/json?fields=formatted_address%2Cname%2Crating%2Copening_hours%2Cgeometry&input=" + model_response +"&inputtype=textquery&key=AIzaSyDgGqGjI0-yZvppdw0XNhdyWR-HPcG1VWE").json()
        print(location)
        if location["status"] == "ZERO_RESULTS":
            return render_template("ai.html",chat_reply="I couldn't find that location, could you try again?")
        r = requests.get("https://maps.googleapis.com/maps/api/place/nearbysearch/json?keyword&location="+ str(location["candidates"][0]["geometry"]["location"]["lat"]) +"%2C"+ str(location["candidates"][0]["geometry"]["location"]["lng"]) +"&radius=1500&type=restaurant&key=AIzaSyDgGqGjI0-yZvppdw0XNhdyWR-HPcG1VWE&business_status=OPERATIONAL").json()
        chat_reply = ""
        #Sort by rank
        for i in r['results']:
            chat_reply += i["name"]
            chat_reply += "\n"
        
        model_response_2 = model.generate_content("Recommend a single resturant from the following list of resturants and provide a brief description fewer than 20 words. Return in the format [You're visiting " + model_response + "! You should try <resturant>, <description>]. Do not use # or * symbols:" + chat_reply).text
        print(model_response_2)
        chat_reply = model_response_2
        return render_template("ai.html",chat_reply=chat_reply)
    else:
        return render_template("ai.html")





@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        with sqlite3.connect("users.db") as con:
            con.row_factory = sqlite3.Row
            db = con.cursor()
            username = request.form.get("username")
            rows = db.execute(
                "SELECT * FROM users WHERE username = ?", (request.form.get("username"),)
            )
        rows = rows.fetchall()
        #'pbkdf2:sha256:600000$gpIiEx5JghROxrJN$3bfc8f2e80c5b21b1a95dd07487ea382321bcbdc7e101a4c703fe7028e3121fa'
        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")





@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        elif not request.form.get("confirmation"):
            return apology("must provide password", 400)

        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match", 400)

        username = request.form.get("username")
        password = generate_password_hash(request.form.get("password"))
        # Query database for username
        with sqlite3.connect("users.db") as con:
            db = con.cursor()
            rows = db.execute(
                "SELECT * FROM users WHERE username = ?", (username,)
            )

        # Ensure username exists and password is correct
        if len(list(rows)) != 0:
            return apology("Username already exists", 400)
        with sqlite3.connect("users.db") as con:
            db = con.cursor()
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (username, password))
            con.commit()
        # Redirect user to home page
        return redirect("/login")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")





@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")





@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    """Change a users password"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure password was submitted
        if not request.form.get("old_password") or not request.form.get("new_password") or not request.form.get("confirmation"):
            return apology("must provide password", 403)

        # Query database for username
        with sqlite3.connect("users.db") as con:
            con.row_factory = sqlite3.Row
            db = con.cursor()
            rows = db.execute(
                "SELECT * FROM users WHERE id = ?", (session["user_id"],)
            )
        rows = rows.fetchall()
        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("old_password")
        ):
            return apology("incorrect password", 403)

        elif request.form.get("new_password") != request.form.get("confirmation"):
            return apology("passwords do not match", 403)

        password = generate_password_hash(request.form.get("new_password"))
        with sqlite3.connect("users.db") as con:
            db = con.cursor()
            db.execute("UPDATE users SET username = ?, hash = ? WHERE id = ?", (rows[0]['username'], password, session['user_id']))
            con.commit()
        # Redirect user to home page
        return redirect("/login")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("change_password.html")
    # return history
    return render_template("change_password.html")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)