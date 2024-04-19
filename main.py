from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import sqlite3
from helpers import apology, login_required
import vertexai
from vertexai.preview.generative_models import GenerativeModel
vertexai.init(project="future-producer-418904")

app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)



@app.route('/', methods=['GET', 'POST'])
@login_required
def main():
    #TODO: create login page
    
    if request.method == "POST":
        chat_request = request.form.get("chat_request")
        gemini_pro_model = GenerativeModel("gemini-1.0-pro")
        model_response = gemini_pro_model.generate_content(chat_request)
        print("model_response\n",model_response)
        return render_template("ai.html",chat_reply=model_response.text)
    else:
        return render_template("ai.html")

@app.route('/beam_calculator', methods=["GET", "POST"])
@login_required
def beam_calculator():
    return render_template("beam_calculator.html")


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