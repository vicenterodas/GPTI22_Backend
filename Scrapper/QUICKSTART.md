# Inicio Rapido

Guia corta para instalar, ejecutar y probar el scraper.

## 1. Instalar

```bash
cd /ruta/al/proyecto
python3 -m venv .venv
source .venv/bin/activate
pip install -r ../requirements.txt
cp .env.example .env
```

## 2. Levantar la API

```bash
source .venv/bin/activate
uvicorn app.main:app --reload
```

URLs utiles:

- `http://localhost:8000`
- `http://localhost:8000/docs`

## 3. Ejecutar scraping por API

```bash
curl -X POST http://localhost:8000/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "source": "chiletrabajos",
    "query": "practica informatica",
    "location": "Santiago",
    "max_pages": 2
  }'
```

## 4. Ver ofertas guardadas

```bash
curl http://localhost:8000/offers
```

Con filtros:

```bash
curl "http://localhost:8000/offers?query=python&location=Santiago"
```

## 5. Ejecutar scraping por consola

```bash
source .venv/bin/activate

python scripts/run_scraper.py \
  --source chiletrabajos \
  --query "practica informatica" \
  --location "Santiago" \
  --max-pages 2
```

## 6. Correr pruebas

```bash
source .venv/bin/activate
pytest
```

Pruebas con conexion a sitios reales:

```bash
RUN_INTEGRATION_TESTS=1 pytest -m integration
```

## Comandos utiles

```bash
# Ver fuentes disponibles desde Python
python -c "from app.scrapers.registry import list_available_scrapers; print(list_available_scrapers())"

# Revisar configuracion
python -c "from app.config import settings; print(settings.DATABASE_URL)"

# Reiniciar base de datos local
rm offers.db
python -c "from app.database import init_db; init_db()"
```

## Problemas comunes

- Si falta un paquete, ejecuta `pip install -r ../requirements.txt`.
- Si el puerto `8000` esta ocupado, usa `uvicorn app.main:app --reload --port 8001`.
- Si la base de datos queda bloqueada, cierra la API o cualquier script que este usando `offers.db`.
- Si un scraper deja de encontrar ofertas, puede que el sitio haya cambiado su HTML.
