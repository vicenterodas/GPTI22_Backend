from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import json

app = Flask(__name__)
CORS(app, origins=["http://localhost:8001"])

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
    conn.commit()
    conn.close()

@app.route('/ofertas', methods=['GET'])
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