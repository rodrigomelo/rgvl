"""
Social Media Profile Collector (Instagram + Facebook)
Tries multiple username patterns to find profiles without login.

Usage:
    python3 social_profiles.py                      # All targets
    python3 social_profiles.py --name "Henrique"    # Specific target
    python3 social_profiles.py --platform instagram  # Only Instagram
    python3 social_profiles.py --platform facebook   # Only Facebook
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

OUTPUT_DIR = PROJECT_ROOT / "collected" / "social"

# Target names with common username patterns
TARGETS = [
    {
        "name": "Rodrigo Gorgulho de Vasconcellos Lanna",
        "pessoa_id": 6,
        "patterns": ["rodrigogorgulho", "rodrigo.lanna", "rodrigolanna", "rgorgulho", "rodrigolannabh"],
    },
    {
        "name": "Edmundo de Vasconcellos Lanna",
        "pessoa_id": 2,
        "patterns": ["edmundolanna", "edmundo.lanna", "elanna", "edmundovasconcellos"],
    },
    {
        "name": "Henrique Gorgulho de Vasconcellos Lanna",
        "pessoa_id": 8,
        "patterns": ["henriquelanna", "henrique.lanna", "henriquelannabh", "henriquegorgulho"],
    },
    {
        "name": "Marcelo Gorgulho de Vasconcellos Lanna",
        "pessoa_id": 9,
        "patterns": ["marcelolanna", "marcelo.lanna", "marcelolannabh", "marcelogorgulho"],
    },
    {
        "name": "Junia Gorgulho de Vasconcellos Lanna",
        "pessoa_id": 10,
        "patterns": ["junialanna", "junia.lanna", "junialannabh"],
    },
    {
        "name": "Luiza Lanna",
        "pessoa_id": 12,
        "patterns": ["luizalanna", "luiza.lanna", "luizalannabh"],
    },
    {
        "name": "Fernanda Lanna",
        "pessoa_id": 13,
        "patterns": ["fernandalanna", "fernanda.lanna"],
    },
    {
        "name": "Alessandra Lanna",
        "pessoa_id": 14,
        "patterns": ["alessandralanna", "alessandra.lanna"],
    },
    {
        "name": "Marcela Lanna",
        "pessoa_id": 18,
        "patterns": ["marcelalanna", "marcela.lanna"],
    },
    {
        "name": "Monica Maria Almeida Lanna",
        "pessoa_id": None,
        "patterns": ["monicaalmeida", "monicalanna", "monica.almeida", "monicaalmeidalanna"],
    },
]


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
}


def check_instagram_profile(client, username):
    """Check if an Instagram profile exists and extract public data."""
    url = f"https://www.instagram.com/{username}/"
    try:
        resp = client.get(url, follow_redirects=True, timeout=15)
        if resp.status_code != 200:
            return None

        # Check if it's a real profile page (not login wall)
        html = resp.text
        if "Sorry, this page isn't available" in html or "Page Not Found" in html:
            return None

        # Extract data from meta tags and page content
        soup = BeautifulSoup(html, "html.parser")
        data = {"username": username, "url": url, "platform": "instagram"}

        # OG meta tags
        og_title = soup.find("meta", property="og:title")
        if og_title:
            data["og_title"] = og_title.get("content", "")

        og_desc = soup.find("meta", property="og:description")
        if og_desc:
            desc = og_desc.get("content", "")
            data["og_description"] = desc
            # Parse followers from description: "X Followers, Y Following, Z Posts"
            followers_match = re.search(r"([\d,]+)\s+Followers", desc)
            if followers_match:
                data["followers"] = followers_match.group(1)
            following_match = re.search(r"([\d,]+)\s+Following", desc)
            if following_match:
                data["following"] = following_match.group(1)
            posts_match = re.search(r"([\d,]+)\s+Posts", desc)
            if posts_match:
                data["posts_count"] = posts_match.group(1)

        og_image = soup.find("meta", property="og:image")
        if og_image:
            data["profile_pic_url"] = og_image.get("content", "")

        # Check if it's likely the right person from bio/title
        data["scraped_at"] = datetime.now().isoformat()
        return data

    except Exception as e:
        print(f"    Error @{username}: {e}")
        return None


def check_facebook_profile(client, username):
    """Check if a Facebook profile exists and extract public data."""
    url = f"https://www.facebook.com/{username}"
    try:
        resp = client.get(url, follow_redirects=True, timeout=15)
        if resp.status_code != 200:
            return None

        html = resp.text
        if "page you requested was removed" in html.lower() or "this page isn't available" in html.lower():
            return None

        soup = BeautifulSoup(html, "html.parser")
        data = {"username": username, "url": url, "platform": "facebook"}

        og_title = soup.find("meta", property="og:title")
        if og_title:
            data["og_title"] = og_title.get("content", "")

        og_desc = soup.find("meta", property="og:description")
        if og_desc:
            data["og_description"] = og_desc.get("content", "")

        og_image = soup.find("meta", property="og:image")
        if og_image:
            data["profile_pic_url"] = og_image.get("content", "")

        data["scraped_at"] = datetime.now().isoformat()
        return data

    except Exception as e:
        print(f"    Error fb/{username}: {e}")
        return None


def save_results(results, target_name, platform):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r'[^a-zA-Z0-9]', '_', target_name)
    filepath = OUTPUT_DIR / f"{safe}_{platform}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"  Saved to {filepath}")


def update_db(profiles):
    """Save found profiles to the profiles table"""
    import importlib
    api_db = importlib.import_module("api.db")
    api_models = importlib.import_module("api.models")
    SessionLocal = api_db.SessionLocal
    Perfil = api_models.Perfil
    session = SessionLocal()
    try:
        for p in profiles:
            platform = p.get("platform", "unknown")
            username = p.get("username", "")
            if not username:
                continue

            existing = session.query(Perfil).filter(
                Perfil.source == platform,
                Perfil.external_id == username
            ).first()

            if existing:
                existing.raw_data = json.dumps(p, ensure_ascii=False)
                existing.updated_at = datetime.now()
                print(f"  Updated {platform}: {username}")
            else:
                perfil = Perfil(
                    source=platform,
                    external_id=username,
                    name=p.get("og_title", ""),
                    bio=p.get("og_description", ""),
                    avatar_url=p.get("profile_pic_url", ""),
                    profile_url=p.get("url", ""),
                    raw_data=json.dumps(p, ensure_ascii=False),
                )
                session.add(perfil)
                print(f"  Added {platform}: {username}")

        session.commit()
    except Exception as e:
        session.rollback()
        print(f"  DB error: {e}")
    finally:
        session.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", help="Filter targets by name")
    parser.add_argument("--platform", choices=["instagram", "facebook", "all"], default="all")
    parser.add_argument("--no-db", action="store_true")
    args = parser.parse_args()

    targets = TARGETS
    if args.name:
        targets = [t for t in targets if args.name.lower() in t["name"].lower()]
        if not targets:
            print(f"No target matching '{args.name}'")
            return

    print(f"🔍 Social Profile Collector — {len(targets)} targets, platform={args.platform}\n")

    client = httpx.Client(headers=HEADERS, follow_redirects=True)
    all_found = []

    try:
        for target in targets:
            name = target["name"]
            print(f"\n📌 {name}")

            for username in target["patterns"]:
                # Instagram
                if args.platform in ("instagram", "all"):
                    print(f"  Checking IG @{username}...", end=" ", flush=True)
                    ig = check_instagram_profile(client, username)
                    if ig:
                        print(f"✅ FOUND — {ig.get('og_title', username)}")
                        all_found.append(ig)
                    else:
                        print("—")
                    time.sleep(2)

                # Facebook
                if args.platform in ("facebook", "all"):
                    print(f"  Checking FB/{username}...", end=" ", flush=True)
                    fb = check_facebook_profile(client, username)
                    if fb:
                        print(f"✅ FOUND — {fb.get('og_title', username)}")
                        all_found.append(fb)
                    else:
                        print("—")
                    time.sleep(2)

    finally:
        client.close()

    # Save results
    if all_found:
        print(f"\n✅ Found {len(all_found)} profiles!")
        for target in targets:
            target_profiles = [p for p in all_found if p.get("username") in target["patterns"]]
            if target_profiles:
                save_results(target_profiles, target["name"], "all")
    else:
        print("\n❌ No profiles found")

    # Update DB
    if all_found and not args.no_db:
        update_db(all_found)


if __name__ == "__main__":
    main()
