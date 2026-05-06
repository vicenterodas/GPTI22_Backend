import sqlite3
import random

def init_db():
    conn = sqlite3.connect('ofertas.db')
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

def populate_db():
    init_db()  # Asegurar que la tabla existe
    conn = sqlite3.connect('ofertas.db')
    cursor = conn.cursor()

    # Datos mock de ofertas
    ofertas_mock = [
        {
            'titulo': 'Práctica en Desarrollo Web',
            'empresa': 'TechCorp',
            'descripcion': 'Desarrollo de aplicaciones web usando React y Node.js.',
            'especialidad': 'Ingeniería de Software',
            'requisitos': 'Conocimientos básicos en HTML, CSS, JS.',
            'enlace': 'https://example.com/oferta1'
        },
        {
            'titulo': 'Práctica en Análisis de Datos',
            'empresa': 'DataInc',
            'descripcion': 'Análisis de datos con Python y Pandas.',
            'especialidad': 'Ciencia de Datos',
            'requisitos': 'Curso de estadística aprobado.',
            'enlace': 'https://example.com/oferta2'
        },
        {
            'titulo': 'Práctica en Redes',
            'empresa': 'NetWorks',
            'descripcion': 'Configuración y mantenimiento de redes.',
            'especialidad': 'Redes y Telecomunicaciones',
            'requisitos': 'Conocimientos en Cisco.',
            'enlace': 'https://example.com/oferta3'
        },
        {
            'titulo': 'Práctica en Ciberseguridad',
            'empresa': 'SecureTech',
            'descripcion': 'Auditorías de seguridad y pentesting.',
            'especialidad': 'Ciberseguridad',
            'requisitos': 'Interés en seguridad informática.',
            'enlace': 'https://example.com/oferta4'
        },
        {
            'titulo': 'Práctica en IA',
            'empresa': 'AI Labs',
            'descripcion': 'Desarrollo de modelos de machine learning.',
            'especialidad': 'Inteligencia Artificial',
            'requisitos': 'Curso de Python.',
            'enlace': 'https://example.com/oferta5'
        }
    ]

    # Insertar datos
    for oferta in ofertas_mock:
        cursor.execute('''
            INSERT INTO ofertas (titulo, empresa, descripcion, especialidad, requisitos, enlace)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (oferta['titulo'], oferta['empresa'], oferta['descripcion'], oferta['especialidad'], oferta['requisitos'], oferta['enlace']))

    conn.commit()
    conn.close()
    print("Base de datos poblada con datos mock.")

if __name__ == '__main__':
    populate_db()