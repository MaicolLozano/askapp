from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import mysql.connector
import os
import bcrypt

app = Flask(__name__)


# configuration
app.secret_key = "askapp"

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="askapp",
    port=3307
)

cursor = db.cursor()

# functions
def get_questions():
    cursor.execute("SELECT * FROM questions")
    questions = cursor.fetchall()
    return questions

def count_users():
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    return count

def count_questions():
    cursor.execute("SELECT COUNT(*) FROM questions")
    count = cursor.fetchone()[0]
    return count


# routes
@app.route("/")
def index():
    if "user_id" in session:
        return render_template("index.html", questions=get_questions())
    else:
        return redirect(url_for("login"))  



@app.route("/contact", methods=["GET", "POST"])
def contact():
    if "user_id" in session:
        if request.method == "POST":
            subject = request.form["subject"]
            message = request.form["message"]
            cursor.execute("INSERT INTO contacts (subject, message, user_id) VALUES (%s, %s, %s)", (subject, message, session["user_id"]))
            db.commit()
            return redirect(url_for("index"))
        return render_template("contact.html")
    else:
        return redirect(url_for("login"))



@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, password_hash))
        db.commit()
        return redirect(url_for("login"))
    
    if "user_id" in session:
        return redirect(url_for("index"))
    return render_template("register.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        if user:
            if bcrypt.checkpw(password.encode("utf-8"), user[3].encode("utf-8")):
                session["user_id"] = user[0]
                return redirect(url_for("index"))
        else:
            return "Invalid email or password"
    return render_template("login.html")



@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("login"))



@app.route("/ask", methods=["GET", "POST"])
def ask():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        image = request.files["image"]
        image_path = os.path.join("static", "images", image.filename)
        image.save(image_path)
        cursor.execute("INSERT INTO questions (title, body, img, user_id) VALUES (%s, %s, %s, %s)", (title, body, image_path, session["user_id"]))
        db.commit()
        return redirect(url_for("index"))
    return render_template("ask.html")


@app.route("/question/<int:question_id>")
def question(question_id):
    cursor.execute("SELECT * FROM questions WHERE id = %s", (question_id,))
    question = cursor.fetchone()
    if question is None:
        return redirect(url_for('index'))
    return render_template("question.html", question=question)



@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        search_term = request.form["search"]
        cursor.execute("SELECT * FROM questions WHERE title LIKE %s OR body LIKE %s", (f"%{search_term}%", f"%{search_term}%"))
        questions = cursor.fetchall()
        return render_template("search.html", questions=questions)
    return render_template("search.html")

@app.route("/admin")
def admin():
    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("admin.html", count_users=count_users(), count_questions=count_questions())

# API

@app.route("/api/questions" , methods=["GET"])
def api_questions():
    if request.method == "GET":
        cursor.execute("SELECT * FROM questions" )
        questions = cursor.fetchall()
        return jsonify(questions)


@app.route("/api/users" , methods=["GET"])
def api_users():
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    return jsonify(users)

@app.route("/api/contacts" , methods=["GET"])
def api_contacts():
    cursor.execute("SELECT * FROM contacts")
    contacts = cursor.fetchall()
    return jsonify(contacts)

@app.route("/api/answers" , methods=["GET"])
def api_answers():
    cursor.execute("SELECT * FROM answers")
    answers = cursor.fetchall()
    return jsonify(answers)


@app.route("/api/questions/<int:question_id>/answers", methods=["GET"])
def api_question_answers(question_id):
    cursor.execute("SELECT * FROM answers WHERE question_id = %s", (question_id,))
    answers = cursor.fetchall()
    return jsonify(answers)


@app.route("/api/users/<int:user_id>/questions", methods=["GET"])
def api_user_questions(user_id):
    cursor.execute("SELECT * FROM questions WHERE user_id = %s", (user_id,))
    questions = cursor.fetchall()
    return jsonify(questions) 

 

if __name__ == "__main__":
    app.run(debug=True)