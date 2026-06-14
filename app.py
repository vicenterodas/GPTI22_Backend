from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3
import secrets
from datetime import datetime

app = Flask(__name__)
CORS(app, origins=["http://localhost:8001"], allow_headers=["Content-Type", "Authorization"])

def get_db_connection():
    conn = sqlite3.connect('ofertas.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS ofertas (
                        id INTEGER PRIMARY KEY,
                        titulo TEXT,
                        empresa TEXT,
                        descripcion TEXT,
                        especialidad TEXT,
                        requisitos TEXT,
                        enlace TEXT
                    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        fecha_registro TEXT NOT NULL
                    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS sesiones (
                        token TEXT PRIMARY KEY,
                        usuario_id INTEGER NOT NULL,
                        creado_en TEXT NOT NULL,
                        FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
                    )''')
    conn.commit()
    conn.close()


def get_usuario_by_token(token):
    if not token:
        return None
    conn = get_db_connection()
    usuario = conn.execute('''
        SELECT usuarios.id, usuarios.nombre, usuarios.email
        FROM sesiones
        JOIN usuarios ON usuarios.id = sesiones.usuario_id
        WHERE sesiones.token = ?
    ''', (token,)).fetchone()
    conn.close()
    return usuario


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else None
        usuario = get_usuario_by_token(token)
        if usuario is None:
            return jsonify({'error': 'Debes iniciar sesión para acceder a este recurso.'}), 401
        request.usuario = dict(usuario)
        return f(*args, **kwargs)
    return decorated


@app.route('/register', methods=['POST'])
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


@app.route('/login', methods=['POST'])
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


@app.route('/logout', methods=['POST'])
def logout():
    auth_header = request.headers.get('Authorization', '')
    token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else None
    if token:
        conn = get_db_connection()
        conn.execute('DELETE FROM sesiones WHERE token = ?', (token,))
        conn.commit()
        conn.close()
    return jsonify({'message': 'Sesión cerrada correctamente.'})


@app.route('/me', methods=['GET'])
@login_required
def me():
    return jsonify(request.usuario)


@app.route('/ofertas', methods=['GET'])
@login_required
def get_ofertas():
    especialidad = request.args.get('especialidad', '')
    conn = get_db_connection()
    if especialidad:
        ofertas = conn.execute('SELECT * FROM ofertas WHERE especialidad LIKE ?', ('%' + especialidad + '%',)).fetchall()
    else:
        ofertas = conn.execute('SELECT * FROM ofertas').fetchall()
    conn.close()
    return jsonify([dict(oferta) for oferta in ofertas])

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5002, debug=True)
