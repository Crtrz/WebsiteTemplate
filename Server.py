import sqlite3
import re
from string import punctuation
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import hashlib

Server = Flask(__name__)
Server.secret_key = 'LXtDCX7aMQG1e3tqDPDJTVxXD'

def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        email TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        fullname TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()

# Register a new user
@Server.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    confirmPassword = data.get("confirmPassword")
    fullname = data.get("name")

    if not re.fullmatch(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', email):
        return jsonify({"success": False, "error": "Email address is invalid."}), 400

    #//Password Validation\\#
    if len(password) < 6 or len(password) > 20:
        return jsonify({"success": False, "error": "Password must be between 6-20 letters."}), 400
    if not re.compile('[^a-zA-Z0-9 ]').findall(password):
        return jsonify({"success": False, "error": "Password must include a special character."}), 400

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM users WHERE email = ?", (email,))
    existing_user = cursor.fetchone()

    if existing_user:
        return jsonify({"success": False, "error": "Email already exists. Please choose another."}), 400

    if password != confirmPassword:
        return jsonify({"success": False, "error": "Passwords do not match."}), 400

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute("INSERT INTO users (email, password, fullname) VALUES (?, ?, ?)",
                   (email, hashed_password, fullname))
    conn.commit()
    conn.close()

    session['UserData'] = [email, fullname]
    return jsonify({"success": True})

# Login the user
@Server.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    remember = data.get("remember")

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    Account = cursor.fetchone()

    if  not Account:
        return jsonify({"success": False, "error": "Account does not exist."}), 401

    Email, Password, FullName = Account
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    if hashed_password == Password:
        session['UserData'] = [Email, FullName]

        if remember:
            session.permanent = True
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Password is incorrect."}), 401

@Server.route("/logout")
def logout():
    if 'UserData' in session:
        session.pop('UserData', None)
    return redirect(url_for('LoginPage'))

#ROOT#
@Server.route("/")
def root():
    return redirect(url_for('HomePage'))

@Server.errorhandler(404)
def page_not_found(error):
    return redirect(url_for('root'))

##//Pages\\##
@Server.route("/home")
def HomePage():
    if 'UserData' in session:
        return render_template("Home.html", user=session["UserData"])
    else:
        return redirect(url_for('LoginPage'))

@Server.route("/login")
def LoginPage():
    if 'UserData' in session:
        return redirect(url_for('HomePage'))
    return render_template("Login.html")

@Server.route("/dashboard")
def DashboardPage():
    if 'UserData' not in session:
        return redirect(url_for('HomePage'))
    return "Dashboard Page"

@Server.route("/account")
def AccountSettingsPage():
    if 'UserData' not in session:
        return redirect(url_for('HomePage'))
    return "Account Settings Page"

@Server.route("/carbonfootprint")
def CarbonFootPrintPage():
    return "Carbon footprint calculator"

@Server.route("/energyusage")
def EnergyUsagePage():
    return "Energy Usage"

@Server.route("/blog")
def BlogPage():
    return "Blog"

@Server.route("/consultations")
def ConsultationsPage():
    if 'UserData' not in session:
        return redirect(url_for('HomePage'))
    return "Consultations"

init_db()

if __name__ == "__main__":
    Server.run(debug=True)