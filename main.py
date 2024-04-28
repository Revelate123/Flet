import flask
from flask import Flask, flash, redirect, render_template, request, session, jsonify
import vertexai.generative_models
from werkzeug.security import check_password_hash, generate_password_hash
import requests
import sqlite3
from helpers import apology, login_required
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)


from user import User
import vertexai
import google.oauth2.credentials
import google_auth_oauthlib.flow
from oauth2client import tools
from google.oauth2 import service_account
from google.cloud import datastore
import googleapiclient.discovery
from db import init_db_command
import os





credentials = service_account.Credentials.from_service_account_file(
    'future-producer-418904-5b9b595c6c5e.json')

vertexai.init(credentials=credentials)


model = vertexai.generative_models.GenerativeModel("gemini-pro")

# -*- coding: utf-8 -*-


# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.
CLIENT_SECRETS_FILE = 'client_secret_319728086235-ubuom2fs3laa07rgohgqr9m4mqe00sbc.apps.googleusercontent.com.json'

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ["openid", "https://www.googleapis.com/auth/userinfo.profile",  "https://www.googleapis.com/auth/userinfo.email"]

app = flask.Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)
# Note: A secret key is included in the sample so that it works.
# If you use this code in your application, replace this with a truly secret
# key. See https://flask.palletsprojects.com/quickstart/#sessions.
app.secret_key = 'REPLACE ME - this value is here as a placeholder.'


# Naive database setup
try:
    init_db_command()
except sqlite3.OperationalError:
    # Assume it's already been created
    pass


@app.route('/')
def index():
  return print_index_table()


@app.route('/test')
@login_required
def test_api_request():
  # Load credentials from the session.
  credentials = service_account.Credentials.from_service_account_file(
    'future-producer-418904-5b9b595c6c5e.json')

  vertexai.init(credentials=credentials)

  model = vertexai.generative_models.GenerativeModel("gemini-pro")
  chat_request = "Im from Auckland"
  model_response = model.generate_content("Extract and return as text, only one location from the following sentence. Do not return any other text and do not provide a full stop.:" + chat_request).text
        #If they did not provide a location then I need a way to know
  print(model_response)
  # Save credentials back to session in case access token was refreshed.
  # ACTION ITEM: In a production app, you likely want to save these
  #              credentials in a persistent database instead.

  return (model_response + print_index_table())


@app.route('/authorize')
def authorize():
  flask.session.clear()
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
  print("credentials", credentials)
  info = googleapiclient.discovery.build("oauth2","v2",credentials=credentials)
  info = info.userinfo().get().execute()

  user = User(id_= info["id"], name=info["given_name"], email=info["email"], profile_pic=info["picture"],
              token=credentials.token, refresh_token=credentials.refresh_token, token_uri=credentials.token_uri,
              client_id=credentials.client_id, client_secret=credentials.client_secret, scopes=credentials.scopes)
  if not User.get(info["id"]):
        User.create(id_= info["id"], name=info["given_name"], email=info["email"], profile_pic=info["picture"],
              token=credentials.token, refresh_token=credentials.refresh_token, token_uri=credentials.token_uri,
              client_id=credentials.client_id, client_secret=credentials.client_secret, scopes=credentials.scopes)

  login_user(user)
  
  #flask.session['credentials'] = credentials_to_dict(credentials)

  return flask.redirect(flask.url_for('test_api_request'))


@app.route('/revoke')
@login_required
def revoke():
  user = current_user
  #credentials = google.oauth2.credentials.Credentials(**flask.session['credentials'])
  credentials = google.oauth2.credentials.Credentials(**user.credentials)
  revoke = requests.post('https://oauth2.googleapis.com/revoke',
      params={'token': credentials.token},
      headers = {'content-type': 'application/x-www-form-urlencoded'})

  status_code = getattr(revoke, 'status_code')
  if status_code == 200:
    return('Credentials successfully revoked.' + print_index_table())
  else:
    return('An error occurred.' + print_index_table())


@app.route('/clear')
def clear_credentials():
  if 'credentials' in flask.session:
    del flask.session['credentials']
  return ('Credentials have been cleared.<br><br>' +
          print_index_table())


def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}

def print_index_table():
  return ('<table>' +
          '<tr><td><a href="/test">Test an API request</a></td>' +
          '<td>Submit an API request and see a formatted JSON response. ' +
          '    Go through the authorization flow if there are no stored ' +
          '    credentials for the user.</td></tr>' +
          '<tr><td><a href="/authorize">Test the auth flow directly</a></td>' +
          '<td>Go directly to the authorization flow. If there are stored ' +
          '    credentials, you still might not be prompted to reauthorize ' +
          '    the application.</td></tr>' +
          '<tr><td><a href="/revoke">Revoke current credentials</a></td>' +
          '<td>Revoke the access token associated with the current user ' +
          '    session. After revoking credentials, if you go to the test ' +
          '    page, you should see an <code>invalid_grant</code> error.' +
          '</td></tr>' +
          '<tr><td><a href="/clear">Clear Flask session credentials</a></td>' +
          '<td>Clear the access token currently stored in the user session. ' +
          '    After clearing the token, if you <a href="/test">test the ' +
          '    API request</a> again, you should go back to the auth flow.' +
          '</td></tr></table>')


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)




if __name__ == '__main__':
  # When running locally, disable OAuthlib's HTTPs verification.
  # ACTION ITEM for developers:
  #     When running in production *do not* leave this option enabled.
  os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

  # Specify a hostname and port that are set as a valid redirect URI
  # for your API project in the Google API Console.
  app.run('localhost', 8080)
