from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(
        app,
        origins=["http://localhost:8001", "https://gpti22-practicas360.netlify.app"],
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )

    from app.routers.ofertas import ofertas_bp
    from app.routers.auth import auth_bp
    from app.routers.main import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(ofertas_bp)

    return app
