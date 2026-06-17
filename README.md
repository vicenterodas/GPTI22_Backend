# Plataforma de Prácticas Profesionales

Este es un prototipo funcional básico de una plataforma web centralizada para buscar prácticas profesionales utilizando web scraping (simulado con datos mock).

## Estructura del Proyecto

- `backend/`: API REST en Python con Flask.
- `frontend/`: Interfaz web en HTML/CSS/JS con Bootstrap.

## Cómo Ejecutar

Los endpoints están documentados en [DOCUMENTATION](./DOCUMENTATION.md).

1. Asegúrate de tener Python 3.12 instalado.
   Entorno virtual para Linux/Ubuntu:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Instala las dependencias del backend:
   ```
   pip install -r requirements.txt
   ```

3. Ejecuta el backend:
   ```
   python run.py
   ```
   El backend correrá en http://127.0.0.1:5002

4. Para llenar la database con datos mock:
   ```
   python populate_db.py
   ```

5. En otra terminal, ejecuta el frontend:
   ```
   cd frontend
   python -m http.server 8001
   ```
   El frontend estará disponible en http://localhost:8001
