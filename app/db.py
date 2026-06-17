import sqlite3

DB_PATH = "ofertas.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS ofertas (
            id TEXT PRIMARY KEY,
            activa INTEGER DEFAULT 1,
                 
            titulo TEXT,
            empresa TEXT,
            descripcion TEXT,
                 
            ubicacion TEXT,
            modalidad TEXT,
            area TEXT,
            nivel TEXT,
                 
            fecha_publicacion DATE,
            fecha_expiracion DATE,
                 
            link TEXT,
            salario TEXT,
            duracion TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            fecha_registro TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS sesiones (
            token TEXT PRIMARY KEY,
            usuario_id INTEGER NOT NULL,
            creado_en TEXT NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    """)

    conn.commit()
    conn.close()
    