import os

class Config:
    # 数据库路径
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'chat_history.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 禁用信号系统，以避免性能开销
    SECRET_KEY = os.urandom(24)
    UPLOAD_DIR = os.path.join(BASE_DIR, "data")
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB
