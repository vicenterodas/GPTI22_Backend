# Scraper de Ofertas Laborales

Aplicacion en Python para buscar y guardar ofertas laborales desde portales de empleo.

## Que incluye

- API con FastAPI.
- Base de datos SQLite.
- Scrapers para Chiletrabajos, Computrabajo y Get on Board.
- Filtros por texto, ubicacion, fuente y fecha.
- Script de consola para ejecutar busquedas sin levantar la API.
- Pruebas con pytest.

## Requisitos

- Python 3.11 o superior.
- pip.

## Instalacion

```bash
cd /ruta/al/proyecto
python3 -m venv .venv
source .venv/bin/activate
pip install -r ../requirements.txt
cp .env.example .env
```

El archivo `.env` es opcional. Si no existe, la aplicacion usa valores por defecto.

## Ejecutar la API

```bash
source .venv/bin/activate
uvicorn app.main:app --reload
```

Luego abre:

- API: `http://localhost:8000`
- Documentacion: `http://localhost:8000/docs`

## Endpoints principales

```bash
# Ver estado de la API
curl http://localhost:8000/

# Listar ofertas guardadas
curl http://localhost:8000/offers

# Buscar ofertas guardadas
curl "http://localhost:8000/offers?query=python&location=Santiago"

# Ejecutar scraping
curl -X POST http://localhost:8000/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "source": "chiletrabajos",
    "query": "practica informatica",
    "location": "Santiago",
    "max_pages": 2
  }'
```

## Ejecutar desde consola

```bash
source .venv/bin/activate

python scripts/run_scraper.py \
  --source chiletrabajos \
  --query "practica informatica" \
  --location "Santiago" \
  --max-pages 2
```

## Fuentes disponibles

- `chiletrabajos`
- `computrabajo`
- `getonbrd`

## Pruebas

```bash
source .venv/bin/activate
pytest
```

Para ejecutar pruebas que usan sitios reales:

```bash
RUN_INTEGRATION_TESTS=1 pytest -m integration
```

## Estructura general

```text
app/
  api/        Endpoints de la API
  scrapers/   Scrapers por portal
  services/   Logica de negocio
  utils/      Utilidades
tests/        Pruebas
scripts/      Scripts de consola
```

## Configuracion

Variables comunes en `.env`:

```ini
DATABASE_URL=sqlite:///./offers.db
SCRAPER_DELAY_SECONDS=2
SCRAPER_TIMEOUT_SECONDS=10
RUN_INTEGRATION_TESTS=false
```

## Notas

- La base de datos `offers.db` se crea automaticamente.
- Las ofertas duplicadas se evitan usando la fuente y la URL original.
- El scraping depende de la estructura HTML de cada sitio, por lo que puede requerir ajustes si los portales cambian.
