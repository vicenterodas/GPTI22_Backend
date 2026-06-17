from flask import Blueprint, jsonify

main_bp = Blueprint("main", __name__)


@main_bp.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Bienvenid@ a Prácticas UC",
        "status": "ok",
        "service": "API de ofertas de prácticas",
    })