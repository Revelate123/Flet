from flask_login import UserMixin

from db import get_db

class User(UserMixin):
    def __init__(self, id_, name, email, profile_pic, token, refresh_token, token_uri, client_id, client_secret, scopes):
        self.id = id_
        self.name = name
        self.email = email
        self.profile_pic = profile_pic
        self.token = token
        self.refresh_token = refresh_token
        self.token_uri = token_uri
        self.client_id = client_id
        self.client_secret = client_secret
        self.scopes = scopes

    @staticmethod
    def get(user_id):
        db = get_db()
        user = db.execute(
            "SELECT * FROM user WHERE id = ?", (user_id,)
        ).fetchone()
        if not user:
            return None

        user = User(
            id_=user[0], name=user[1], email=user[2], profile_pic=user[3], token=user[4], 
            refresh_token=user[5], token_uri=user[6], client_id=user[7], client_secret=user[8], scopes=user[9]
        )
        return user

    @staticmethod
    def create(id_, name, email, profile_pic, token, refresh_token, token_uri, client_id, client_secret, scopes):
        db = get_db()
        db.execute(
            "INSERT INTO user (id, name, email, profile_pic, token, refresh_token, token_uri, client_id, client_secret, scopes) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (id_, name, email, profile_pic, token, refresh_token, token_uri, client_id, client_secret, scopes),
        )
        db.commit()