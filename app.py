from flask import Flask, render_template, request, redirect, url_for, flash, session, Response, jsonify
import os
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import subprocess
from functools import wraps
import openai

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

# ---------- OpenAI API ----------
openai.api_key = os.getenv("OPENAI_API_KEY")

# ---------- Database ----------
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
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
    return redirect(url_for("login"))

# -------- Signup --------
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

# -------- Login --------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
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

# -------- Home --------
@app.route("/home")
@login_required
def home():
    return render_template("home.html")

# -------- Logout --------
@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("login"))

# -------- About, Contact, Services --------
@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/services")
@login_required
def services():
    # Keep page render logic as-is (no blocking API call here)
    return render_template("services.html")

# -------- Service info (AJAX: returns JSON) --------
@app.route("/service_info_json", methods=["POST"])
@login_required
def service_info_json():
    data = request.get_json(silent=True) or {}
    topic = data.get("topic", "").strip()
    if not topic:
        return jsonify({"error": "Topic is required."}), 400

    try:
        # Ask for a structure that is easy to format on the frontend
        prompt = (
            f"You are a helpful recipe assistant for a website. "
            f"Write professional content about: {topic}. "
            f"Start with a concise description (2–4 sentences). "
            f"Then provide 6–10 clear numbered steps. "
            f"Do not use bullets or symbols like *, #, - anywhere."
        )

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful recipe assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )
        content = response.choices[0].message.content

        return jsonify({"content": content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------- Generator --------
@app.route("/generator")
@login_required
def generator():
    return render_template("index1.html")

# -------- Stream: ChatGPT recipe --------
@app.route("/stream")
@login_required
def stream():
    ingredients = request.args.get("ingredients", "")
    if not ingredients:
        return "⚠️ Please provide ingredients.", 400

    def generate():
        try:
            stream = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful recipe assistant. Always answer step by step."},
                    {"role": "user", "content": f"Create a detailed step-by-step recipe using these ingredients: {ingredients}. Do not use *, #, -."}
                ],
                stream=True
            )
            for chunk in stream:
                if chunk.choices[0].delta.get("content"):
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"\n❌ Error generating recipe: {e}"

    return Response(generate(), mimetype="text/plain")

# ---------- Run ----------
if __name__ == "__main__":
    app.run(debug=True)
