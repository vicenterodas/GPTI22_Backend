import json
import os
import subprocess
import sys
import uuid
from pathlib import Path

from app.db import get_db_connection


ROOT_DIR = Path(__file__).resolve().parent.parent
EXPORT_SCRIPT = ROOT_DIR / "Scrapper" / "scripts" / "export_scraped_offers.py"


def _env(name, default=None):
    return os.getenv(name, os.getenv(name.replace("SCRAPER_", "SCRAPPER_"), default))


def _scraper_command(
    query=None,
    location=None,
    date_range=None,
    max_pages=None,
    sources=None,
):
    command = [
        sys.executable,
        str(EXPORT_SCRIPT),
        "--query",
        query or _env("SCRAPER_SYNC_QUERY", "practica"),
        "--max-pages",
        str(max_pages or _env("SCRAPER_SYNC_MAX_PAGES", "3")),
    ]

    location = location or _env("SCRAPER_SYNC_LOCATION")
    if location:
        command.extend(["--location", location])

    date_range = date_range or _env("SCRAPER_SYNC_DATE_RANGE")
    if date_range:
        command.extend(["--date-range", date_range])

    sources = sources or _env("SCRAPER_SYNC_SOURCES")
    if sources:
        command.extend(["--sources", sources])

    return command


def _to_app_offer(scraper_offer):
    title = scraper_offer.get("title")
    link = scraper_offer.get("source_url")

    if not title or not link:
        return None

    return {
        "id": str(uuid.uuid4()),
        "titulo": title,
        "empresa": scraper_offer.get("company") or "Sin empresa",
        "descripcion": scraper_offer.get("description"),
        "ubicacion": scraper_offer.get("location"),
        "modalidad": scraper_offer.get("job_type"),
        "area": scraper_offer.get("source"),
        "nivel": None,
        "fecha_publicacion": scraper_offer.get("published_date"),
        "fecha_expiracion": None,
        "link": link,
        "salario": None,
        "duracion": None,
        "activa": 1,
    }


def _insert_missing_offers(offers):
    inserted = 0
    skipped = 0

    conn = get_db_connection()
    try:
        for raw_offer in offers:
            offer = _to_app_offer(raw_offer)
            if offer is None:
                skipped += 1
                continue

            existing = conn.execute(
                "SELECT id FROM ofertas WHERE link = ?",
                (offer["link"],),
            ).fetchone()

            if existing:
                skipped += 1
                continue

            conn.execute(
                """
                INSERT INTO ofertas (
                    id,
                    titulo, empresa, descripcion, ubicacion,
                    modalidad, area, nivel,
                    fecha_publicacion, fecha_expiracion,
                    link, salario, duracion,
                    activa
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    offer["id"],
                    offer["titulo"],
                    offer["empresa"],
                    offer["descripcion"],
                    offer["ubicacion"],
                    offer["modalidad"],
                    offer["area"],
                    offer["nivel"],
                    offer["fecha_publicacion"],
                    offer["fecha_expiracion"],
                    offer["link"],
                    offer["salario"],
                    offer["duracion"],
                    offer["activa"],
                ),
            )
            inserted += 1

        conn.commit()
    finally:
        conn.close()

    return inserted, skipped


def sync_scraper_offers(
    query=None,
    location=None,
    date_range=None,
    max_pages=None,
    sources=None,
):
    if _env("SCRAPER_SYNC_ENABLED", "true").lower() in ("0", "false", "no"):
        return {"enabled": False, "inserted": 0, "skipped": 0, "errors": []}

    timeout = int(_env("SCRAPER_SYNC_TIMEOUT_SECONDS", "60"))

    try:
        completed = subprocess.run(
            _scraper_command(
                query=query,
                location=location,
                date_range=date_range,
                max_pages=max_pages,
                sources=sources,
            ),
            cwd=str(ROOT_DIR / "Scrapper"),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except Exception as exc:
        return {"enabled": True, "inserted": 0, "skipped": 0, "errors": [str(exc)]}

    if completed.returncode != 0:
        return {
            "enabled": True,
            "inserted": 0,
            "skipped": 0,
            "errors": [completed.stderr or completed.stdout],
        }

    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        return {
            "enabled": True,
            "inserted": 0,
            "skipped": 0,
            "errors": [f"Invalid scraper JSON: {exc}"],
        }

    inserted, skipped = _insert_missing_offers(payload.get("offers", []))

    return {
        "enabled": True,
        "inserted": inserted,
        "skipped": skipped,
        "errors": payload.get("errors", []),
        "scraper_results": payload.get("results", []),
    }
