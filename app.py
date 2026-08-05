from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from ai_engine import ask_ai
from models import db, User, ChatHistory, ChatSession
from werkzeug.security import generate_password_hash, check_password_hash

from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")

AI_MODEL = os.getenv("AI_MODEL")

database_url = os.getenv("DATABASE_URL")

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db.init_app(app)

with app.app_context():
    db.create_all()

# ================= LOGIN =================app

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")


        user = User.query.filter_by(username=username).first()


        if user and check_password_hash(user.password, password):

            session["username"] = user.username

            return redirect(url_for("dashboard"))

        return render_template(
    "login.html",
    error="Invalid Username or Password"
)


    return render_template("login.html")





# ================= REGISTER =================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        fullname = request.form.get("fullname")
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")

        print("Fullname:", fullname)
        print("Email:", email)
        print("Username:", username)
        print("Password:", password)


        if User.query.filter_by(username=username).first():
            return "Username already exists"


        if User.query.filter_by(email=email).first():
            return "Email already exists"



        hashed_password = generate_password_hash(password)



        user = User(
            fullname=fullname,
            email=email,
            username=username,
            password=hashed_password
        )


        db.session.add(user)
        db.session.commit()


        return redirect(url_for("login"))


    return render_template("register.html")






# ================= DASHBOARD =================

@app.route("/dashboard")
def dashboard():

    if "username" not in session:
        return redirect(url_for("login"))


    return render_template(
        "dashboard.html",
        username=session["username"]
    )



# ================= PROFILE =================

@app.route("/profile")
def profile():

    if "username" not in session:
        return redirect(url_for("login"))

    user = User.query.filter_by(username=session["username"]).first()

    return render_template(
        "profile.html",
        user=user
    )


# ================= LOGOUT =================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))

# ================= CHATBOT =================

@app.route("/chatbot")
def chatbot():

    if "username" not in session:
        return redirect(url_for("login"))

    return render_template(
        "chatbot.html",
        username=session["username"]
    )

# ================= CHAT =================

@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()
    message = data.get("message", "")

    reply = ask_ai(
        message,
        model=AI_MODEL
    )

    if "username" in session:

        user = User.query.filter_by(
            username=session["username"]
        ).first()

        if user:

            session_id = session.get("chat_session_id")

            if not session_id:

                new_session = ChatSession(
                    user_id=user.id,
                    title=message[:40]
                )

                db.session.add(new_session)
                db.session.commit()

                session["chat_session_id"] = new_session.id
                session_id = new_session.id

            chat = ChatHistory(
                user_id=user.id,
                session_id=session_id,
                message=message,
                response=reply
            )

            db.session.add(chat)
            db.session.commit()

    return jsonify({
        "reply": reply
    })


@app.route("/chat-sessions")
def chat_sessions():

    if "username" not in session:
        return jsonify([])

    user = User.query.filter_by(
        username=session["username"]
    ).first()

    if not user:
        return jsonify([])

    sessions = ChatSession.query.filter_by(
        user_id=user.id
    ).order_by(
        ChatSession.created_at.desc()
    ).all()

    return jsonify([
        {
            "id": s.id,
            "title": s.title
        }
        for s in sessions
    ])

@app.route("/chat-history")
def chat_history():

    if "username" not in session:
        return jsonify([])

    user = User.query.filter_by(
        username=session["username"]
    ).first()

    if not user:
        return jsonify([])

    session_id = session.get("chat_session_id")

    if not session_id:
        return jsonify([])
    
    query = ChatHistory.query.filter_by(
        user_id=user.id
    )

    if session_id:
        query = query.filter_by(
            session_id=session_id
        )

    chats = query.order_by(
        ChatHistory.created_at.asc()
    ).all()

    history = []

    for chat in chats:
        history.append({
            "id": chat.id,
            "message": chat.message,
            "response": chat.response,
            "created_at": str(chat.created_at)
        })

    return jsonify(history)

@app.route("/new-chat", methods=["POST"])
def new_chat():

    session.pop("chat_session_id", None)

    return jsonify({
        "success": True
    })

@app.route("/select-chat/<int:session_id>")
def select_chat(session_id):

    session["chat_session_id"] = session_id

    return jsonify({
        "success": True
    })

# ================= EMAIL WRITER =================

@app.route("/email-writer")
def email_writer():

    if "username" not in session:
        return redirect(url_for("login"))


    return render_template("email_writer.html")






@app.route("/generate-email", methods=["POST"])
def generate_email():

    data = request.get_json()


    prompt = f"""
Write a professional email.

Receiver:
{data.get("receiver")}

Purpose:
{data.get("purpose")}

Details:
{data.get("details")}

Only give email content.
"""


    reply = ask_ai(
        prompt,
        model=AI_MODEL
    )


    return jsonify({
        "email": reply
    })








# ================= CODING ASSISTANT =================

@app.route("/coding")
def coding():

    if "username" not in session:
        return redirect(url_for("login"))

    return render_template("coding_assistant.html")


@app.route("/generate-code", methods=["POST"])
def generate_code():

    data = request.get_json()

    prompt = f"""
Generate code.

Programming Language:
{data.get("language")}

Problem:
{data.get("request")}

Give code with explanation.
"""

    reply = ask_ai(
        prompt,
        model=AI_MODEL
    )

    return jsonify({
        "code": reply
    })







# ================= TRANSLATOR =================

@app.route("/translator")
def translator():

    if "username" not in session:
        return redirect(url_for("login"))


    return render_template("translator.html")







@app.route("/translate", methods=["POST"])
def translate():

    data = request.get_json()


    text = data.get("text", "")
    language = data.get("language", "Telugu")



    if text.strip() == "":
        return jsonify({
            "translation": "Enter text"
        })



    prompt = f"""
You are a professional English to Telugu translator.

Translate the given sentence.

Rules:
- Understand meaning.
- Use natural Telugu.
- Do not explain.
- Do not add extra words.
- Output only translation.

English:
{text}

Telugu:
"""



    reply = ask_ai(
        prompt,
        model=AI_MODEL
    )



    return jsonify({
        "translation": reply.strip()
    })



# ================= DOCUMENT GENERATOR =================

@app.route("/document-generator")
def document_generator():

    if "username" not in session:
        return redirect(url_for("login"))

    return render_template("document_generator.html")



@app.route("/generate-document", methods=["POST"])
def generate_document():

    data = request.get_json()

    topic = data.get("topic", "")
    document_type = data.get("type", "Report")
    details = data.get("details", "")


    prompt = f"""
Create a professional {document_type} document.

Topic:
{topic}

Details:
{details}

Requirements:
- Use proper headings.
- Make it clear and professional.
- Provide complete content.
"""


    reply = ask_ai(
        prompt,
        model=AI_MODEL
    )


    return jsonify({
        "document": reply
    })







# ================= DATA ANALYSIS =================

@app.route("/data-analysis")
def data_analysis():

    if "username" not in session:
        return redirect(url_for("login"))

    return render_template("data_analysis.html")



@app.route("/analyze-data", methods=["POST"])
def analyze_data():

    data = request.get_json()

    dataset = data.get("data", "")


    prompt = f"""
Analyze the given data.

Provide:
- Summary
- Important patterns
- Insights
- Possible conclusions

Data:
{dataset}
"""


    reply = ask_ai(
        prompt,
        model=AI_MODEL
    )


    return jsonify({
        "analysis": reply
    })



# ================= START APP =================

print(app.url_map)

if __name__ == "__main__":


    with app.app_context():

        db.create_all()


    app.run(host="127.0.0.1", port=5000, debug=True)