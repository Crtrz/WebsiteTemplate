import datetime
import sqlite3
import re
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import hashlib
from datetime import datetime

Server = Flask(__name__)
Server.secret_key = 'LXtDCX7aMQG1e3tqDPDJTVxXD'

def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        email TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        fullname TEXT NOT NULL
    )''')

    # Carbon Footprint Entries
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS carbon_footprint (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT,
        date TEXT,
        emissions REAL,
        notes TEXT,
        FOREIGN KEY(user_email) REFERENCES users(email)
    )''')

    # Energy Usage
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS energy_usage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT,
        month TEXT,
        usage REAL,
        difference REAL,
        FOREIGN KEY(user_email) REFERENCES users(email)
    )''')

    # Consultations
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS consultations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT,
        date TEXT,
        time TEXT,
        topic TEXT,
        FOREIGN KEY(user_email) REFERENCES users(email)
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

@Server.route('/submit_carbon', methods=['POST'])
def submit_carbon():
    if 'UserData' not in session:
        return redirect(url_for('LoginPage'))

    email = session['UserData'][0]
    data = request.get_json()

    date = data.get('date')
    emissions = data.get('emissions')
    notes = data.get('notes')

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO carbon_footprint (user_email, date, emissions, notes)
        VALUES (?, ?, ?, ?)
    ''', (email, date, emissions, notes))
    conn.commit()
    conn.close()

    return jsonify({"success": True})

@Server.route('/consultationsAPI', methods=['POST'])
def Consultations():
    if 'UserData' not in session:
        return redirect(url_for('LoginPage'))

    email = session['UserData'][0]
    data = request.get_json()

    date_str = data.get('date')
    time = data.get('time')
    topic = data.get('topic')

    try:
        consultation_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        if consultation_date < datetime.today().date():
            return jsonify({"success": False, "error": "Date must be today or in the future."})
    except ValueError:
        return jsonify({"success": False, "error": "Invalid date format."})

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO consultations (user_email, date, time, topic)
        VALUES (?, ?, ?, ?)
    ''', (email, date_str, time, topic))
    conn.commit()
    conn.close()

    return jsonify({"success": True})


@Server.route('/consultationsAPI', methods=['GET'])
def get_consultations():
    if 'UserData' not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401

    email = session['UserData'][0]

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT date, time, topic FROM consultations WHERE user_email = ?", (email,))
    rows = cursor.fetchall()
    conn.close()

    consultations = [{"date": r[0], "time": r[1], "topic": r[2]} for r in rows]
    print({"success": True, "consultations": consultations})
    return jsonify({"success": True, "consultations": consultations})


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

@Server.route('/dashboard')
def DashboardPage():
    if 'UserData' not in session:
        return redirect(url_for('LoginPage'))

    email = session["UserData"][0]
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('SELECT date, emissions, notes FROM carbon_footprint WHERE user_email = ?', (email,))
    carbon_results = [
        {"date": row[0], "emissions": row[1], "notes": row[2]}
        for row in cursor.fetchall()
    ]

    cursor.execute('SELECT month, usage, difference FROM energy_usage WHERE user_email = ? ORDER BY id DESC LIMIT 1', (email,))
    row = cursor.fetchone()
    energy_usage = {"last_month": row[1], "difference": row[2]} if row else {"last_month": 0, "difference": 0}

    # Load consultations
    cursor.execute('SELECT date, time, topic FROM consultations WHERE user_email = ?', (email,))
    consultations = [
        {"date": row[0], "time": row[1], "topic": row[2]}
        for row in cursor.fetchall()
    ]

    conn.close()

    return render_template("Dashboard.html",user=session["UserData"],carbon_results=carbon_results,energy_usage=energy_usage,consultations=consultations)


@Server.route("/account")
def AccountSettingsPage():
    if 'UserData' not in session:
        return redirect(url_for('HomePage'))
    return "Account Settings Page"

@Server.route("/carbonfootprint")
def CarbonFootPrintPage():
    if 'UserData' not in session:
        return redirect(url_for('HomePage'))
    return render_template("CarbonFootPrint.html", user=session["UserData"])

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
    return render_template("Consultations.html", user=session["UserData"])

init_db()

if __name__ == "__main__":
    Server.run(host='0.0.0.0', port=5000, debug=True)
