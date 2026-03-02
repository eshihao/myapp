# from flask_sqlalchemy import SQLAlchemy

# db = SQLAlchemy()

# class ChatHistory(db.Model):
#     __tablename__ = 'chat_history'
    
#     id = db.Column(db.Integer, primary_key=True)
#     user_message = db.Column(db.String(500), nullable=False)
#     bot_message = db.Column(db.String(500), nullable=False)
#     timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    
#     def __init__(self, user_message, bot_message):
#         self.user_message = user_message
#         self.bot_message = bot_message
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()



class Conversation(db.Model):
    __tablename__ = "conversation"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), default="新对话")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    messages = db.relationship(
        "ChatMessage",
        backref="conversation",
        lazy=True,
        cascade="all, delete-orphan"
    )

    npy_files = db.relationship(
        "NpyFile",
        backref="conversation",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Conversation {self.id}>"
    


class ChatMessage(db.Model):
    __tablename__ = "chat_message"

    id = db.Column(db.Integer, primary_key=True)

    conversation_id = db.Column(
        db.Integer,
        db.ForeignKey("conversation.id"),
        nullable=False
    )

    role = db.Column(
        db.String(20),
        nullable=False
    )  # user / assistant / system

    content = db.Column(
        db.Text,
        nullable=False
    )

    timestamp = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def __repr__(self):
        return f"<ChatMessage {self.id} {self.role}>"




class NpyFile(db.Model):
    __tablename__ = "npy_file"

    id = db.Column(db.Integer, primary_key=True)

    conversation_id = db.Column(
        db.Integer,
        db.ForeignKey("conversation.id"),
        nullable=True
    )

    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(500), nullable=False)

    shape = db.Column(db.String(100))
    dtype = db.Column(db.String(50))

    uploaded_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def __repr__(self):
        return f"<NpyFile {self.filename}>"
