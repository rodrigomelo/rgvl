#!/usr/bin/env python3
"""
DETRAN-MG Vehicles Collector
Queries vehicle registrations via DETRAN-MG public portal.

NOTE: Full vehicle data requires CPF + birth date for vehicle consultation.
This collector attempts to find accessible vehicle data and notes what's needed.

Targets:
  - Rodrigo Gorgulho de Vasconcellos Lanna (CPF: 314.516.326-49)
  - Rosália Fagundes Ladeira (CPF: 359.959.806-10)

Usage:
    python3 collectors/detran_mg_vehicles.py                    # All targets
    python3 collectors/detran_mg_vehicles.py --no-db           # Skip DB write
    python3 collectors/detran_mg_vehicles.py --cpf 314.516.326-49  # Specific
"""

import argparse
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import httpx
from bs4 import BeautifulSoup

OUTPUT_DIR = PROJECT_ROOT / "collected" / "detran_mg"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

TARGETS = [
    {
        "name": "Rodrigo Gorgulho de Vasconcellos Lanna",
        "person_id": 6,
        "cpf": "314.516.326-49",
    },
    {
        "name": "Rosália Fagundes Ladeira",
        "person_id": 7,
        "cpf": "359.959.806-10",
    },
]


def get_birth_date_from_cpf(cpf: str) -> str | None:
    """Try to extract or look up birth date for a CPF."""
    # We don't have birth dates from CPF alone
    # This would need to be stored in the DB or provided manually
    return None


def check_portal_access(client):
    """Check if DETRAN-MG portal is accessible."""
    urls_to_try = [
        "https://portalservicos.detran.mg.gov.br/",
        "https://www.detran.mg.gov.br/",
        "https://portalservicos.detran.mg.gov.br/veiculos/consulta",
    ]
    for url in urls_to_try:
        try:
            resp = client.get(url, timeout=10, follow_redirects=True)
            if resp.status_code == 200:
                return url, resp.text
        except Exception:
            continue
    return None, None


def find_vehicle_consultation_endpoints(html, base_url):
    """Parse the portal page to find vehicle consultation links."""
    soup = BeautifulSoup(html, "html.parser")
    endpoints = []

    # Look for forms and links related to vehicles
    for form in soup.find_all("form"):
        action = form.get("action", "")
        if "veiculo" in action.lower() or "veic" in action.lower() or "consulta" in action.lower():
            endpoints.append(action if action.startswith("http") else base_url.rstrip("/") + action)

    for link in soup.find_all("a", href=True):
        href = link.get("href", "")
        if any(kw in href.lower() for kw in ["veiculo", "veic", "placa", "consulta-veiculo"]):
            full_url = href if href.startswith("http") else base_url.rstrip("/") + href
            endpoints.append(full_url)

    return list(set(endpoints))


def save_results(data, target_cpf):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r'[^0-9]', '', target_cpf)
    filepath = OUTPUT_DIR / f"cpf_{safe}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  Saved to {filepath}")


def update_db_vehicle(vehicle_data, target_name, person_id, source_url):
    """Save vehicle records to the vehicles table."""
    import importlib
    api_db = importlib.import_module("api.db")
    api_models = importlib.import_module("api.models")
    SessionLocal = api_db.SessionLocal
    Vehicle = api_models.Veiculo
    session = SessionLocal()
    try:
        for v in vehicle_data:
            plate = v.get("plate", "")
            if not plate:
                continue

            existing = session.query(Vehicle).filter(
                Vehicle.person_id == person_id,
                Vehicle.plate == plate
            ).first()

            if existing:
                for key, val in v.items():
                    if hasattr(existing, key) and key not in ("id", "person_id"):
                        setattr(existing, key, val)
                existing.collected_at = datetime.utcnow()
                print(f"  Updated vehicle: {plate}")
            else:
                vehicle = Vehicle(
                    person_id=person_id,
                    plate=v.get("plate"),
                    vin=v.get("vin"),
                    make_model=v.get("make_model"),
                    year_manufactured=v.get("year"),
                    model_year=v.get("model_year"),
                    color=v.get("color"),
                    fuel=v.get("fuel"),
                    city=v.get("city"),
                    state=v.get("state"),
                    status=v.get("status"),
                    source=source_url,
                    raw_data=json.dumps(v, ensure_ascii=False),
                )
                session.add(vehicle)
                print(f"  Added vehicle: {plate} — {v.get('make_model', '?')}")

        session.commit()
    except Exception as e:
        session.rollback()
        print(f"  DB error: {e}")
    finally:
        session.close()


def main():
    parser = argparse.ArgumentParser(description="DETRAN-MG Vehicles Collector")
    parser.add_argument("--no-db", action="store_true", help="Skip DB write")
    parser.add_argument("--cpf", help="Filter by CPF")
    args = parser.parse_args()

    targets = TARGETS
    if args.cpf:
        targets = [t for t in targets if t["cpf"] == args.cpf]
        if not targets:
            print(f"No target with CPF '{args.cpf}'")
            return

    print(f"🚗 DETRAN-MG Vehicles Collector — {len(targets)} targets\n")

    client = httpx.Client(headers=HEADERS, follow_redirects=True, timeout=20)

    try:
        print("🌐 Checking DETRAN-MG portal access...")
        base_url, portal_html = check_portal_access(client)

        if base_url is None:
            print("  ❌ DETRAN-MG portal is not accessible")
            print("  Note: Portal may be blocking automated requests")
            return

        print(f"  ✅ Portal accessible at: {base_url}")

        # Find vehicle consultation endpoints
        if portal_html:
            endpoints = find_vehicle_consultation_endpoints(portal_html, base_url)
            if endpoints:
                print(f"  📋 Found {len(endpoints)} vehicle-related endpoints:")
                for ep in endpoints[:5]:
                    print(f"     - {ep}")

        # For each target, note what's needed for vehicle search
        print("\n📌 Vehicle Search Requirements:")
        for target in targets:
            cpf_clean = re.sub(r'[^0-9]', '', target["cpf"])
            print(f"\n  {target['name']}")
            print(f"  CPF: {target['cpf']}")
            print(f"  ❗ Full vehicle search requires: CPF + Birth Date (DD/MM/YYYY)")

            # Try to find vehicle data from public sources
            print(f"\n  Checking public vehicle registries...")

            # The DETRAN-MG vehicle consultation at:
            # https://portalservicos.detran.mg.gov.br/veiculos/consulta-veiculo
            # requires authentication with CPF + birth date
            #
            # Alternative: Check if any vehicle plates are already known
            # or try to search by plate

            result = {
                "target": target["name"],
                "cpf": target["cpf"],
                "person_id": target["person_id"],
                "portal_url": base_url,
                "vehicle_consultation_url": "https://portalservicos.detran.mg.gov.br/veiculos/consulta-veiculo",
                "requires": {
                    "cpf": target["cpf"],
                    "birth_date": "DD/MM/YYYY (NOT available — need to add manually)",
                },
                "found_vehicles": [],
                "searched_at": datetime.now().isoformat(),
            }

            save_results(result, target["cpf"])

            print(f"\n  ⚠️  ACTION REQUIRED: To query vehicles, we need the birth date of {target['name']}")
            print(f"      Birth date format: DD/MM/YYYY")
            print(f"      Once available, vehicle data will be at:")
            print(f"      {result['vehicle_consultation_url']}")

    finally:
        client.close()

    print("\n✅ DETRAN-MG vehicle scan complete")


if __name__ == "__main__":
    main()
