import uuid
import sqlite3
from datetime import date, timedelta

DB_PATH = "ofertas.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn


def create_mock_data():
    hoy = date.today()

    return [
        (
            str(uuid.uuid4()),
            1,
            "Práctica Data Science",
            "TechCorp",
            "Trabajo con modelos de ML y datos",
            "Santiago",
            "Remota",
            "Data",
            "Practica",
            str(hoy),
            str(hoy + timedelta(days=30)),
            "https://techcorp.com/practica-ds",
            "600000",
            "3 meses"
        ),
        (
            str(uuid.uuid4()),
            1,
            "Práctica Backend Python",
            "SoftSolutions",
            "Desarrollo de APIs en Flask",
            "Santiago",
            "Híbrida",
            "Ingeniería",
            "Practica",
            str(hoy),
            str(hoy + timedelta(days=60)),
            "https://softsolutions.com/backend",
            "500000",
            "6 meses"
        ),
        (
            str(uuid.uuid4()),
            1,
            "Práctica Marketing Digital",
            "MarketLab",
            "Gestión de campañas digitales",
            "Remoto",
            "Remota",
            "Marketing",
            "Practica",
            str(hoy),
            str(hoy + timedelta(days=45)),
            "https://marketlab.com/practica",
            "450000",
            "4 meses"
        ),
        (
            str(uuid.uuid4()),
            1,
            "Práctica Frontend React",
            "WebStudio",
            "Interfaces modernas con React",
            "Valparaíso",
            "Híbrida",
            "Ingeniería",
            "Practica",
            str(hoy),
            str(hoy + timedelta(days=90)),
            "https://webstudio.com/frontend",
            "550000",
            "6 meses"
        )
    ]


def populate():
    conn = get_connection()
    cursor = conn.cursor()

    data = create_mock_data()

    cursor.executemany("""
        INSERT INTO ofertas (
            id,
            activa,
            titulo,
            empresa,
            descripcion,
            ubicacion,
            modalidad,
            area,
            nivel,
            fecha_publicacion,
            fecha_expiracion,
            link,
            salario,
            duracion
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, data)

    conn.commit()
    conn.close()

    print(f"✔ Insertadas {len(data)} ofertas mock")


if __name__ == "__main__":
    populate()