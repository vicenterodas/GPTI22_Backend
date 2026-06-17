from flask import Blueprint, request, jsonify
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)
from datetime import datetime
import secrets

from app.db import get_db_connection
from app.auth import login_required

auth_bp = Blueprint(
    "auth",
    __name__
)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json(silent=True) or {}
    nombre = (data.get('nombre') or '').strip()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    if not nombre or not email or not password:
        return jsonify({'error': 'Nombre, correo y contraseña son obligatorios.'}), 400

    if len(password) < 6:
        return jsonify({'error': 'La contraseña debe tener al menos 6 caracteres.'}), 400

    conn = get_db_connection()
    existente = conn.execute('SELECT id FROM usuarios WHERE email = ?', (email,)).fetchone()
    if existente:
        conn.close()
        return jsonify({'error': 'Ya existe una cuenta con ese correo.'}), 409

    password_hash = generate_password_hash(password)
    fecha_registro = datetime.now().isoformat()
    conn.execute(
        'INSERT INTO usuarios (nombre, email, password_hash, fecha_registro) VALUES (?, ?, ?, ?)',
        (nombre, email, password_hash, fecha_registro)
    )
    conn.commit()
    conn.close()

    return jsonify({'message': 'Cuenta creada correctamente. Ya puedes iniciar sesión.'}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    if not email or not password:
        return jsonify({'error': 'Correo y contraseña son obligatorios.'}), 400

    conn = get_db_connection()
    usuario = conn.execute('SELECT * FROM usuarios WHERE email = ?', (email,)).fetchone()

    if usuario is None or not check_password_hash(usuario['password_hash'], password):
        conn.close()
        return jsonify({'error': 'Correo o contraseña incorrectos.'}), 401

    token = secrets.token_hex(32)
    conn.execute(
        'INSERT INTO sesiones (token, usuario_id, creado_en) VALUES (?, ?, ?)',
        (token, usuario['id'], datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

    return jsonify({
        'token': token,
        'nombre': usuario['nombre'],
        'email': usuario['email'],
        'fecha_registro': usuario['fecha_registro']
    })


@auth_bp.route('/logout', methods=['POST'])
def logout():
    auth_header = request.headers.get('Authorization', '')
    token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else None
    if token:
        conn = get_db_connection()
        conn.execute('DELETE FROM sesiones WHERE token = ?', (token,))
        conn.commit()
        conn.close()
    return jsonify({'message': 'Sesión cerrada correctamente.'})


@auth_bp.route('/me', methods=['GET'])
@login_required
def me():
    return jsonify(request.usuario)

