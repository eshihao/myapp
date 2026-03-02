from flask import Flask, render_template
from config import Config
from models import db
from routes.upload_routes import upload_bp
from routes.chat_routes import chat_bp
from routes.visualize_routes import visualize_bp
from routes.conversation_routes import conversation_bp

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

app.register_blueprint(upload_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(visualize_bp)
app.register_blueprint(conversation_bp)

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True,port=5011)
