from functools import wraps
from flask import request, jsonify
from app.db import get_db_connection


def get_usuario_by_token(token):
    if not token:
        return None

    conn = get_db_connection()

    usuario = conn.execute("""
        SELECT usuarios.id, usuarios.nombre, usuarios.email
        FROM sesiones
        JOIN usuarios
            ON usuarios.id = sesiones.usuario_id
        WHERE sesiones.token = ?
    """, (token,)).fetchone()

    conn.close()

    return usuario


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")

        token = (
            auth_header.split(" ")[1]
            if auth_header.startswith("Bearer ")
            else None
        )

        usuario = get_usuario_by_token(token)

        if usuario is None:
            return jsonify({
                "error": "Debes iniciar sesión para acceder a este recurso."
            }), 401

        request.usuario = dict(usuario)

        return f(*args, **kwargs)

    return decorated