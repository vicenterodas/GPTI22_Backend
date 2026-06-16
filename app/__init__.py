from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app, origins=["http://localhost:8001"])

    from app.routers.ofertas import ofertas_bp
    from app.routers.main import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(ofertas_bp)

    return app