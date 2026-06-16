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
    conn.commit()
    conn.close()
    