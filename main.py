import flask
from flask import Flask, flash, redirect, render_template, request, session, jsonify, send_file
import vertexai.generative_models
import requests
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
    UserMixin
)
from flask_sqlalchemy import SQLAlchemy
import vertexai
import google.oauth2.credentials
import google_auth_oauthlib.flow
from google.oauth2 import service_account
import googleapiclient.discovery
import os
import dotenv


dotenv.load_dotenv()


def create_app(test_config=None):


  #credentials = service_account.Credentials.from_service_account_file(
      #'future-producer-418904-5b9b595c6c5e.json')

  #vertexai.init(credentials=credentials)


  #model = vertexai.generative_models.GenerativeModel("gemini-pro")

  # -*- coding: utf-8 -*-


  # This variable specifies the name of a file that contains the OAuth 2.0
  # information for this application, including its client_id and client_secret.
  #CLIENT_SECRETS_FILE = 'client_secret_2_319728086235-ubuom2fs3laa07rgohgqr9m4mqe00sbc.apps.googleusercontent.com.json'
  #CLIENT_SECRETS_FILE = os.environ.get('CLIENT_SECRETS_FILE')

  CLIENT_SECRETS_FILE = {"web":{"client_id":os.environ.get("client_id_C"),
                                "project_id":os.environ.get("project_id_C"),
                                "auth_uri":os.environ.get("auth_uri_C"),
                                "token_uri":os.environ.get("token_uri_C"),
                                "auth_provider_x509_cert_url":os.environ.get("auth_provider_x509_cert_url_C"),
                                "client_secret":os.environ.get("client_secret_C"),
                                "redirect_uris":os.environ.get("redirect_uris_C")
                                }}
  # This OAuth 2.0 access scope allows for full read/write access to the
  # authenticated user's account and requires requests to use an SSL connection.
  SCOPES = ["openid", "https://www.googleapis.com/auth/userinfo.profile",  "https://www.googleapis.com/auth/userinfo.email"]

  #FUTURE_PRODUCER = 'future-producer-418904-ed3008c258c5.json'
  #FUTURE_PRODUCER = os.environ.get('FUTURE_PRODUCER')
  
  FUTURE_PRODUCER = {
  "type": os.environ.get("type_F"),
  "project_id": os.environ.get("project_id_F"),
  "private_key_id": os.environ.get("private_key_id_F"),
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDzTN1O6GMUDlj/\nJYUBg+FdIxUz+G0LGGYRaNpr/iseSCC+XpAvBhoPj0NrcpaD/okyQvdkpVIg7/As\n4IgobLfhaGSS5iXDUr5BPMwx7R3EN/hqh/q9sfIifzcoK4oZ/xyJvUtjqsKRTImD\ngjLC2bNmyRE3MJpxXewINKJRiWUMGvPZChCHSrbRNpkSDMgvFcjXNavAjhVUXQNI\nyNF5SoDWGeK3l4l2JbI/mD9aDTVAnIfT8bQSwI234pr4bdiOprnQjdNkFljZqhZV\nLw2YES7/xjQLXp0hU1NJft5Bzm9pgZsiXE/mhZT7Lnt9UIMCORfjPwIVc98lSRFg\nJWvKJjQbAgMBAAECggEADcuZ8NN0arq1iSITfJaBvMo0dZHsfOiRQQN0/xKWV003\nrhOmkUQDTkaNSBZjOnDATr1FUcud8IgqUiEZF1Gyy3Ej4sBx+7VBXGmaGmqbeXjC\n+SdkrETeud4Evp5ZYkf40kaNc8VG6v4v/ejv/+RgK7/S3hI/b5Ynv/9cBMuJkzoH\ns9rE7qpLhDN7MQZbNnMvLfq1VSPeREra5wdQkKJ5RKm3sYFeGD6aiDAdLk0U0pOK\n9wnNS8VP1Y7CGEfeF+WKYL097xaHn7MfFJBTTAKptaRg4b5tgbm1Xwwet+jqAzEK\nipwDfdV+Vj/3wuDPPfhQXaQzgrhFO87FTiA70TqT4QKBgQD8O6DmJOwnEfWGtNxs\nP3vwRtzzJFDO4gs3qzAp5lzN8kAzIl6OdMWwBwT+MhNA0rQVheB8U3qkqHUeY2Zr\nzkWJxEm9tdeY/M1rRyPz+345SowdadKFqHK9ORhjEKMOGdeZXSl2AfLePgaWMVO2\nDksIRecLc30HxKIHKcfKGjZnxQKBgQD27xVW7U60OayVf4clUYl5sHUm2Mfs4Hfg\n+twyL8qSKEKm0X+NfrWEpYRHmnSkQ3IfdSUJEXzGaryZCBR9BqyJLIiEKNbzPWVu\nulAAPIrZlEpyzJU8qbTVZFhORdy2LY8oX51ZoLdaKqwHRVWpfTEjUhNEsSKozTmQ\nWc7BRsgKXwKBgEcW6z9SMrjESAYCXYmozt6mqklg9+GHNhAnkHiOs6Nb3ppK2ome\nAcWeBNs78882U4kpZV7FDHDyBahd7ZT+2vx8NShh4vT8c00EDO8L98Rf7WOw2qPP\nGR+ZwvTQ0JP91pUj+7aF0BSxOJwGJQjPuHgJc5f3ocqZse0A6o1cm+7dAoGBAOds\n6NYAMCvuhZXS4GkUQsCepR0UPEL/mLpswWPzsGlMfDL10xJcN2iq6w9kbX7pixJ6\naoxWLFeU/0546SLH13n0F7mswM9UsjSVPpcKJqOGPEPdAtzIvCbmFXC+Pv0qM6oF\n+mVen5hMt89UptTi9OOCb3aIgNAtDo7/7Crt2FsHAoGARRWxTp/tBLKyoo4hcRVm\nHnNuG1ww1wAuMyFlAUGv9Or4CBQimhFDTrAagFj20ibmexAHbQgQu+A703GCVOcX\nr2Vg2unTt/92Bo6yKJ1JXaza6Z/wpS+oFjuF4RdqwyC+JsJRNBFZW3J96XLuLQMz\nHut0II5PIcfCk5W9vPQLeBE=\n-----END PRIVATE KEY-----\n",
  "client_email": os.environ.get("client_email_F"),
  "client_id": os.environ.get("client_id_F"),
  "auth_uri": os.environ.get("auth_uri_F"),
  "token_uri": os.environ.get("token_uri_F"),
  "auth_provider_x509_cert_url": os.environ.get("auth_provider_x509_cert_url_F"),
  "client_x509_cert_url": os.environ.get("client_x509_cert_url_F"),
  "universe_domain": os.environ.get("universe_domain_F")
  }



  app = flask.Flask(__name__)
  
  app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
  login_manager = LoginManager()
  login_manager.init_app(app)
  # Note: A secret key is included in the sample so that it works.
  # If you use this code in your application, replace this with a truly secret
  # key. See https://flask.palletsprojects.com/quickstart/#sessions.
  app.secret_key = 'REPLACE ME - this value is here as a placeholder.'



  db = SQLAlchemy(app)
  login = LoginManager(app)
  login.login_view = 'login'

  class User(UserMixin, db.Model):
      __tablename__ = 'users'
      id = db.Column(db.Integer, primary_key=True)
      username = db.Column(db.String(64), nullable=False)
      email = db.Column(db.String(64), nullable=True)


  @login.user_loader
  def load_user(id):
      return db.session.get(User, int(id))


  @app.route('/')
  @login_required
  def index():
    return flask.redirect(flask.url_for('restaurant'))
    #return print_index_table()



  @app.route('/cv')
  @login_required
  def cv():
    
          return send_file('static\Thomas Duffett CV (1).pdf', mimetype='.pdf')



  @app.route('/restaurant', methods=["GET","POST"])
  @login_required
  def restaurant():
    # Load credentials from the session.
    
    if request.method == "POST":
          #return ('<div>' + FUTURE_PRODUCER["private_key"] + '</div>')
          credentials = service_account.Credentials.from_service_account_info(
            FUTURE_PRODUCER)

          print(credentials)
          vertexai.init(credentials=credentials)
          model = vertexai.generative_models.GenerativeModel("gemini-pro")
          chat_request = request.form.get("chat_request")
          model_response = model.generate_content(chat_request)
          print("model_response\n",model_response)
          model_response = model.generate_content("Extract and return as text, only one location from the following sentence. Do not return any other text and do not provide a full stop.:" + chat_request).text
          #If they did not provide a location then I need a way to know
          print(model_response)
          location = requests.get("https://maps.googleapis.com/maps/api/place/findplacefromtext/json?fields=formatted_address%2Cname%2Crating%2Copening_hours%2Cgeometry&input=" + model_response +"&inputtype=textquery&key=AIzaSyDgGqGjI0-yZvppdw0XNhdyWR-HPcG1VWE").json()
          print(location)
          if location["status"] == "ZERO_RESULTS":
              return render_template("restaurant.html",chat_reply="I couldn't find that location, could you try again?")
          r = requests.get("https://maps.googleapis.com/maps/api/place/nearbysearch/json?keyword&location="+ str(location["candidates"][0]["geometry"]["location"]["lat"]) +"%2C"+ str(location["candidates"][0]["geometry"]["location"]["lng"]) +"&radius=1500&type=restaurant&key=AIzaSyDgGqGjI0-yZvppdw0XNhdyWR-HPcG1VWE&business_status=OPERATIONAL").json()
          chat_reply = ""
          #Sort by rank
          for i in r['results']:
              chat_reply += i["name"]
              chat_reply += "\n"
          model_response_2 = model.generate_content("Recommend a single resturant from the following list of resturants and provide a brief description fewer than 20 words. Return in the format [You're visiting " + model_response + "! You should try <resturant>, <description>]. Do not use # or * symbols:" + chat_reply).text
          print(model_response_2)
          chat_reply = model_response_2
          return render_template("restaurant.html",chat_reply=chat_reply)
    else:
      return render_template("restaurant.html")
    return (model_response + print_index_table())



  @app.route('/login')
  def login():
    #if user has already authenticated then should just auto log them in.
    return render_template("login.html")


  x = ''
  @app.route('/authorize')
  def authorize():
    flask.session.clear()
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    print(CLIENT_SECRETS_FILE)
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        CLIENT_SECRETS_FILE, scopes=SCOPES)

    # The URI created here must exactly match one of the authorized redirect URIs
    # for the OAuth 2.0 client, which you configured in the API Console. If this
    # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
    # error.
    #flow.redirect_uri = flask.url_for('oauth2callback', _external=True)
    flow.redirect_uri = CLIENT_SECRETS_FILE["web"]["redirect_uris"]
    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')

    # Store the state so the callback can verify the auth server response.
    flask.session["test"] = 'this is a test'
    flask.session['state'] = state
    x = "hello world"
    session.modified = True

    return flask.redirect(authorization_url)


  @app.route('/oauth2callback')
  def oauth2callback():
    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    state = flask.session['state']
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = CLIENT_SECRETS_FILE["web"]["redirect_uris"]

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = flask.request.url.replace("http://","https://")
    print(authorization_response)
    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    credentials = flow.credentials
    print("credentials", credentials)
    info = googleapiclient.discovery.build("oauth2","v2",credentials=credentials)
    info = info.userinfo().get().execute()

    user = db.session.scalar(db.select(User).where(User.id == info["id"]))
    if user is None:
          user = User(email=info["email"], username=info["email"].split('@')[0])
          db.session.add(user)
          db.session.commit()

    login_user(user)
    flask.session['credentials'] = credentials_to_dict(credentials)
    return flask.redirect(flask.url_for('restaurant'))


  @app.route('/logout')
  @login_required
  def revoke():
    logout_user()
    #flash('You have been logged out.')
    credentials = google.oauth2.credentials.Credentials(**flask.session['credentials'])
    if 'credentials' in flask.session:
      del flask.session['credentials']
    revoke = requests.post('https://oauth2.googleapis.com/revoke',
        params={'token': credentials.token},
        headers = {'content-type': 'application/x-www-form-urlencoded'})
    status_code = getattr(revoke, 'status_code')
    if status_code == 200:
      
      return render_template("login.html")
      return('Credentials successfully revoked.' + print_index_table())
    else:
      flash('An error occured.')
      return('An error occurred.' + print_index_table())


  @app.route('/clear')
  def clear_credentials():
    logout_user()
    if 'credentials' in flask.session:
      del flask.session['credentials']
    flash('You have been logged out.')
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


  with app.app_context():
      db.create_all()


  if __name__ == '__main__':
    # When running locally, disable OAuthlib's HTTPs verification.
    # ACTION ITEM for developers:
    #     When running in production *do not* leave this option enabled.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    # Specify a hostname and port that are set as a valid redirect URI
    # for your API project in the Google API Console.
    app.run(host = '0.0.0.0',debug=True)
  return app
   
yourapp = create_app()