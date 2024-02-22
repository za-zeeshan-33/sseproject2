from flask import Flask, render_template, request, redirect, url_for, flash
from flask_cors import CORS
import requests
import os
import json

app = Flask(__name__, static_folder='static')

app.secret_key = 'your_very_secret_key_here'
#session key - need random generator

@app.route("/")
def homepage():
    return render_template("index.html")

@app.route("/submit_register", methods=["POST"])
def submit_register():
    input_username = request.form.get("username")
    input_password = request.form.get("password")
    response = requests.post(f"https://finalprojectsse.azurewebsites.net/api/register?username={input_username}&password={input_password}")
    if response.status_code == 200:
        success_message = response.text
        flash(success_message)
        return redirect(url_for("login"))
    else:
        # Handle error or unsuccessful registration
        # You might want to return an error message or redirect to a different page
        error_message = response.text
        flash(error_message)
        return redirect(url_for("register"))




@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/profile")
def profile():
    return render_template("profile.html")

@app.route('/map')
def index():
    return render_template("map.html")