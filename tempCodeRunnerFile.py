from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import subprocess
from functools import wraps

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

# ---------- Database ----------
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  # change if needed
        database="recipegpt_db"
    )

# ---------- Login required decorator ----------
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

# ---------- Routes ----------
@app.route("/")
def index():
    return redirect(url_for("login"))  # Always go to login first

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirmPassword = request.form.get("confirmPassword")

        if not username or not email or not password or not confirmPassword:
            flash("Please fill in all fields.", "danger")
            return redirect(url_for("signup"))

        if password != confirmPassword:
            flash("Passwords do not match!", "danger")
            return redirect(url_for("signup"))

        hashed_password = generate_password_hash(password)
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                (username, email, hashed_password)
            )
            conn.commit()

            # Optionally send email using PHP
            php_path = "php"
            sendmail_path = os.path.join(os.getcwd(), "sendmail.php")
            subprocess.Popen([php_path, sendmail_path, username, email, password])

            flash("Account created! Please login.", "success")
            return redirect(url_for("login"))
        except mysql.connector.Error as err:
            flash(f"Error: {err}", "danger")
        finally:
            cursor.close()
            conn.close()

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("home"))
        else:
            flash("Invalid email or password.", "danger")

    return render_template("login.html")

@app.route("/home")
@login_required
def home():
    return render_template("home.html")

@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("login"))

# Optional pages
@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/generator")
@login_required
def generator():
    return render_template("index1.html")

# ---------- Run ----------
if __name__ == "__main__":
    app.run(debug=True)
