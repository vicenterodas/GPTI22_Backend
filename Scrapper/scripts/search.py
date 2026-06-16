"""
Interactive script to search for job offers in real-time.
Fetches from Chiletrabajos.cl based on user filters.
Usage: python scripts/search.py
"""

import os
import sys
from pathlib import Path

# Add project root to sys.path so the `app` package can be imported
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.database import SessionLocal
from app.services.scrape_service import ScrapeService


def main():
    print("\n" + "="*60)
    print("🔍 BUSCADOR DE PRÁCTICAS EN VIVO")
    print("="*60 + "\n")
    
    # Input 1: Query
    query = input("¿Qué práctica buscas? (ej: data, ingenieria, psicologia): ").strip()
    if not query:
        print("❌ Debes escribir algo")
        return
    
    # Input 2: Date range
    print("\nRango de fechas:")
    print("  1. Reciente (últimos 3 días)")
    print("  2. Última semana")
    print("  3. Último mes")
    print("  4. Todas (sin filtro)")
    date_choice = input("Elige (1-4): ").strip()
    
    date_map = {
        "1": "recent",
        "2": "last_week",
        "3": "last_month",
        "4": None,
    }
    date_range = date_map.get(date_choice, None)
    
    # Input 3: Location
    print("\nUbicación:")
    print("  1. Santiago")
    print("  2. Valparaíso")
    print("  3. Concepción")
    print("  4. Todas")
    location_choice = input("Elige (1-4): ").strip()
    
    location_map = {
        "1": "Santiago",
        "2": "Valparaíso",
        "3": "Concepción",
        "4": None,
    }
    location = location_map.get(location_choice, None)
    
    # Search in real-time from all enabled scrapers
    from app.scrapers.registry import list_available_scrapers
    from app.services.offer_service import OfferService
    
    db = SessionLocal()
    available_sources = list_available_scrapers()

    deleted_offers = OfferService.delete_all_offers(db)
    print(f"\n🧹 Base reiniciada: {deleted_offers} ofertas anteriores eliminadas.")
    
    print(f"\n🔎 Buscando en {', '.join(available_sources)} en vivo...\n")
    
    all_results = {}
    total_all = 0
    new_all = 0
    duplicates_all = 0
    errors_all = []
    
    # Search in each enabled scraper
    for source in available_sources:
        try:
            result = ScrapeService.scrape_and_save(
                db,
                source=source,
                query=query,
                location=location,
                date_range=date_range,
                max_pages=6
            )
            all_results[source] = result
            total_all += result['total_found']
            new_all += result['new_offers_saved']
            duplicates_all += result['duplicates_skipped']
            errors_all.extend(result.get('errors', []))
        except Exception as e:
            print(f"❌ Error buscando en {source}: {e}")
            errors_all.append(f"{source}: {str(e)}")
    
    if total_all == 0:
        print("❌ No encontramos prácticas con esos criterios\n")
    else:
        print(f"✅ Encontramos {total_all} ofertas totales (nuevas: {new_all}, duplicadas: {duplicates_all})\n")
        for source, result in all_results.items():
            print(f"   - {source}: {result['total_found']} ofertas")
        print("-" * 60)
        
        # Fetch and display the most recently saved offers from all sources combined
        offers = OfferService.get_recent_offers(
            db,
            source=None,  # Get from all sources
            limit=total_all
        )
        
        if not offers:
            print("No hay ofertas guardadas para mostrar aquí.")
        else:
            print("Mostrando las ofertas más recientes guardadas:")
            for i, o in enumerate(offers, 1):
                source_indicator = f" [{o.source}]" if hasattr(o, 'source') else ""
                print(f"\n{i}. {o.title}{source_indicator}")
                print(f"   📌 {o.company}")
                if o.location:
                    print(f"   📍 {o.location}")
                if o.published_date:
                    print(f"   📅 {o.published_date.strftime('%Y-%m-%d')}")
                if getattr(o, 'job_type', None):
                    print(f"   🏷️ {o.job_type}")
                if o.description:
                    desc = o.description[:100] + "..." if len(o.description) > 100 else o.description
                    print(f"   📝 {desc}")
                print(f"   🔗 {o.source_url}")
                print()
        
        print("-" * 60)
    
    if errors_all:
        print("\n⚠️  Errores durante la búsqueda:")
        for error in errors_all:
            print(f"  - {error}")
    
    db.close()
    print()


if __name__ == "__main__":
    main()
