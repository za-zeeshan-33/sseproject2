from flask import Flask, render_template
from flask import request, redirect, url_for, flash, session

import requests

app = Flask(__name__, static_folder='static')

app.secret_key = 'your_very_secret_key_here'


@app.before_request
def before_request():
    session.setdefault('auth_token', None)
    session.setdefault('username', None)


@app.route("/")
def homepage():
    return render_template("index.html")


@app.route("/widget1")
def widget1():
    return render_template("widget1.html")


@app.route("/widget2")
def widget2():
    username = session.get('username')
    return render_template("widget2.html", username=username)


@app.route("/submit_register", methods=["POST"])
def submit_register():
    input_username = request.form.get("username")
    input_password = request.form.get("password")
    response = requests.get(
        f"https://sse-project-2.azure-api.net/login-microservice/register"
        f"?username={input_username}&password={input_password}"
    )
    if response.status_code == 200:
        success_message = response.text
        flash(success_message)
        return redirect(url_for("login"))
    else:
        error_message = response.text
        flash(error_message)
        return redirect(url_for("register"))


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/submit_login", methods=["POST"])
def submit_login():
    input_username = request.form.get("username")
    input_password = request.form.get("password")
    response = requests.get(
        f"https://sse-project-2.azure-api.net/login-microservice/login"
        f"?username={input_username}&password={input_password}"
    )
    if response.status_code == 200:
        token = response.headers.get('Authorization').split(
            ' ')[1] if 'Authorization' in response.headers else None
        if token:
            session['auth_token'] = token
            session['username'] = input_username
            return redirect(url_for("homepage"))
        else:
            flash("Authorization token not found.")
            return redirect(url_for("login"))
    else:
        error_message = response.text
        flash(error_message)
        return redirect(url_for("login"))


@app.route("/login")
def login():
    return render_template("login.html")


@app.route('/logout', methods=['POST'])
def logout():
    token = session.get('auth_token')
    if not token:
        session.pop('auth_token', None)
        session.pop('username', None)
        return redirect(url_for("logoutresult"))

    response = requests.get(
        f"https://sse-project-2.azure-api.net/login-microservice/logout"
        f"?token={token}"
    )
    if response.status_code == 200:
        session.pop('auth_token', None)
        session.pop('username', None)
        error_message = response.text
        flash(error_message)
        return redirect(url_for("logoutresult"))
    else:
        error_message = response.text
        flash(error_message)
        session.pop('auth_token', None)
        session.pop('username', None)
        return redirect(url_for("logoutresult"))


@app.route("/logoutresult")
def logoutresult():
    return render_template("logout.html")


@app.route("/profile")
def profile():
    username = session.get('username')
    token = session.get('auth_token')
    if not token:
        flash("You must be logged in to view your profile.")
        return redirect(url_for("login"))

    response = requests.get(
        f"https://sse-project-2.azure-api.net/login-microservice/protected"
        f"?token={token}"
    )
    if response.status_code == 400:
        return render_template("profile.html", username=username)
    elif response.status_code == 401:
        error_message = response.json().get(
            'message', 'You are not authorized to view this page.')
        flash(error_message)
        return redirect(url_for("login"))
    else:
        flash("An error occurred. Please try again.")
        return redirect(url_for("login"))


@app.route('/map')
def index():
    return render_template("map.html")


@app.route('/country')
def country():
    username = session.get('username')
    return render_template("country.html", username=username)


@app.route('/search')
def search():
    query = request.args.get('query')
    return render_template('searchresult.html', query=query)
