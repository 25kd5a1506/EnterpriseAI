from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"

class ChatSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    title = db.Column(db.String(255), nullable=False)

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

class ChatHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    session_id = db.Column(
        db.Integer,
        db.ForeignKey("chat_session.id"),
        nullable=False
    )

    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )