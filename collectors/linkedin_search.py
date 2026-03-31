#!/usr/bin/env python3
"""
LinkedIn Profile Search Collector
Searches LinkedIn public profiles for RGVL family members.

Usage:
    python3 collectors/linkedin_search.py                 # All targets
    python3 collectors/linkedin_search.py --name Rodrigo  # Specific target
    python3 collectors/linkedin_search.py --no-db        # Skip DB write
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

OUTPUT_DIR = PROJECT_ROOT / "collected" / "linkedin"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}

# LinkedIn username patterns for RGVL family
TARGETS = [
    {
        "name": "Rodrigo Gorgulho de Vasconcellos Lanna",
        "person_id": 6,
        "cpf": "314.516.326-49",
        "patterns": [
            "rodrigo-gorgulho-lanna",
            "rodrigogorgulho",
            "rodrigogorgulholanna",
            "rodrigo-lanna-",
            "rodrigovasconcelloslanna",
        ],
    },
    {
        "name": "Henrique Gorgulho de Vasconcellos Lanna",
        "person_id": 8,
        "patterns": [
            "henrique-gorgulho-lanna",
            "henriquegorgulho",
            "henriquelanna",
            "henrique-lanna-",
        ],
    },
    {
        "name": "Marcelo Gorgulho de Vasconcellos Lanna",
        "person_id": 9,
        "patterns": [
            "marcelo-gorgulho-lanna",
            "marcelogorgulho",
            "marcelolanna",
            "marcelo-lanna-",
        ],
    },
    {
        "name": "Rosália Fagundes Ladeira",
        "person_id": 7,
        "cpf": "359.959.806-10",
        "patterns": [
            "rosalia-fagundes-ladeira",
            "rosalialadeira",
            "rosalia-ladeira",
            "rosaliafagundesladeira",
        ],
    },
    {
        "name": "Edmundo de Vasconcellos Lanna",
        "person_id": 2,
        "patterns": [
            "edmundo-vasconcellos-lanna",
            "edmundolanna",
            "edmundo-lanna-",
        ],
    },
]


def check_linkedin_profile(client, username):
    """Check if a LinkedIn profile exists and extract public data."""
    url = f"https://www.linkedin.com/in/{username}/"
    try:
        resp = client.get(url, follow_redirects=True, timeout=15)
        status = resp.status_code

        if status == 999:
            # LinkedIn blocking
            return {"username": username, "url": url, "status": "blocked", "platform": "linkedin"}

        if status == 404:
            return None

        if status != 200:
            return None

        html = resp.text
        if "Page not found" in html or "page not found" in html.lower():
            return None
        if "security verification" in html.lower() or "captcha" in html.lower():
            return {"username": username, "url": url, "status": "captcha", "platform": "linkedin"}

        soup = BeautifulSoup(html, "html.parser")
        data = {"username": username, "url": url, "platform": "linkedin", "status": "found"}

        # Extract name from title
        title_tag = soup.find("title")
        if title_tag:
            title = title_tag.get_text(strip=True)
            data["page_title"] = title
            # LinkedIn titles are like "FirstName LastName | Title at Company"
            if "|" in title:
                data["full_name"] = title.split("|")[0].strip()

        # Extract description
        og_desc = soup.find("meta", property="og:description")
        if og_desc:
            data["description"] = og_desc.get("content", "")

        # Extract profile image
        og_image = soup.find("meta", property="og:image")
        if og_image:
            data["profile_image"] = og_image.get("content", "")

        # Extract LinkedIn member ID if present
        app_link = soup.find("link", rel="preconnect", href=re.compile("linkedin.com"))
        if app_link:
            href = app_link.get("href", "")
            if "/mi/n/" in href:
                match = re.search(r"/mi/n/([^?]+)", href)
                if match:
                    data["member_id"] = match.group(1)

        data["scraped_at"] = datetime.now().isoformat()
        return data

    except httpx.TimeoutException:
        return {"username": username, "url": url, "status": "timeout", "platform": "linkedin"}
    except Exception as e:
        return {"username": username, "url": url, "status": f"error: {e}", "platform": "linkedin"}


def save_results(results, target_name):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r'[^a-zA-Z0-9]', '_', target_name)
    filepath = OUTPUT_DIR / f"{safe}_linkedin.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"  Saved to {filepath}")


def update_db(profiles, targets):
    """Save found profiles to the profiles table."""
    import importlib
    api_db = importlib.import_module("api.db")
    api_models = importlib.import_module("api.models")
    SessionLocal = api_db.SessionLocal
    Profile = api_models.Perfil
    session = SessionLocal()
    try:
        for p in profiles:
            if p.get("status") != "found":
                continue
            username = p.get("username", "")
            if not username:
                continue

            # Find matching target
            target = None
            for t in targets:
                if username in t.get("patterns", []):
                    target = t
                    break

            existing = session.query(Profile).filter(
                Profile.source == "linkedin",
                Profile.external_id == username
            ).first()

            if existing:
                existing.raw_data = json.dumps(p, ensure_ascii=False)
                existing.updated_at = datetime.utcnow()
                print(f"  Updated linkedin: {username}")
            else:
                profile = Profile(
                    source="linkedin",
                    external_id=username,
                    name=p.get("full_name", ""),
                    bio=p.get("description", ""),
                    profile_url=p.get("url", ""),
                    avatar_url=p.get("profile_image", ""),
                    raw_data=json.dumps(p, ensure_ascii=False),
                )
                session.add(profile)
                print(f"  Added linkedin: {username} — {p.get('full_name', '?')}")

        session.commit()
    except Exception as e:
        session.rollback()
        print(f"  DB error: {e}")
    finally:
        session.close()


def main():
    parser = argparse.ArgumentParser(description="LinkedIn Profile Search Collector")
    parser.add_argument("--name", help="Filter targets by name")
    parser.add_argument("--no-db", action="store_true", help="Skip DB write")
    args = parser.parse_args()

    targets = TARGETS
    if args.name:
        targets = [t for t in targets if args.name.lower() in t["name"].lower()]
        if not targets:
            print(f"No target matching '{args.name}'")
            return

    print(f"🔍 LinkedIn Profile Collector — {len(targets)} targets\n")

    client = httpx.Client(headers=HEADERS, follow_redirects=True, timeout=20)
    all_found = []

    try:
        for target in targets:
            name = target["name"]
            print(f"\n📌 {name}")

            for username in target["patterns"]:
                print(f"  Checking linkedin.com/in/{username}...", end=" ", flush=True)
                result = check_linkedin_profile(client, username)

                if result is None:
                    print("— (not found)")
                elif result.get("status") == "found":
                    print(f"✅ FOUND — {result.get('full_name', username)}")
                    all_found.append(result)
                elif result.get("status") == "blocked":
                    print("🚫 BLOCKED (LinkedIn anti-bot)")
                elif result.get("status") == "captcha":
                    print("🔒 CAPTCHA required")
                elif result.get("status") == "timeout":
                    print("⏱️ TIMEOUT")
                else:
                    print(f"⚠️ {result.get('status', 'unknown')}")

                time.sleep(3)  # LinkedIn is aggressive with rate limits

    finally:
        client.close()

    if all_found:
        print(f"\n✅ Found {len(all_found)} LinkedIn profiles!")
        for target in targets:
            target_profiles = [p for p in all_found if p.get("username") in target.get("patterns", [])]
            if target_profiles:
                save_results(target_profiles, target["name"])

        if not args.no_db:
            update_db(all_found, targets)
    else:
        print("\n❌ No LinkedIn profiles found")


if __name__ == "__main__":
    main()
