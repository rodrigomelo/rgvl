#!/usr/bin/env python3
"""
RGVL Collector Orchestrator
Runs all (or selected) collectors in sequence.

Usage:
    python3 run_all.py                    # Run all collectors
    python3 run_all.py --only web         # Run only web_search collector
    python3 run_all.py --skip twitter     # Skip twitter collector
    python3 run_all.py --list             # List available collectors
"""

import argparse
import importlib
import sys
import time
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Collector registry: name -> (module_path, class_name, description)
COLLECTORS = {
    "local":            ("data.collectors.local",            "LocalCollector",         "Load local structured data files"),
    "import_structured": ("data.collectors.import_structured", "ImportStructuredCollector", "Import structured JSON/CSV data"),
    "email":             ("data.collectors.mail_collector",   "EmailCollector",         "Scan Gmail for family documents"),
    "father_drive":      ("data.collectors.father_drive",     "FatherDriveCollector",   "Extract docs from father's Google Drive"),
    "github":            ("data.collectors.github",           "GithubCollector",        "Search GitHub for mentions"),
    "web_search":        ("data.collectors.web_search",       "WebSearchCollector",     "Search web for name mentions"),
    "twitter":           ("data.collectors.twitter",          "TwitterCollector",       "Search X/Twitter for mentions"),
    "social_profiles":   ("data.collectors.social_profiles",  "SocialProfilesCollector","Find Instagram/Facebook profiles"),
    "jucemg":            ("data.collectors.jucemg",           "JuceMGCollector",        "Search JUCEMG company registry"),
    "jucesp":            ("data.collectors.jucesp",           "JucespCollector",        "Search JUCESP company registry"),
    "tjmg":              ("data.collectors.tjmg",             "TjmgCollector",          "Search TJMG legal processes"),
    "tjsp":              ("data.collectors.tjsp",             "TjspCollector",          "Search TJSP legal processes"),
}


def list_collectors():
    """Print available collectors."""
    print("\n📋 Available Collectors:\n")
    for name, (_, _, desc) in sorted(COLLECTORS.items()):
        print(f"  {name:20s} — {desc}")
    print(f"\n  Total: {len(COLLECTORS)} collectors\n")


def run_collector(name):
    """Run a single collector by name."""
    if name not in COLLECTORS:
        print(f"  ❌ Unknown collector: {name}")
        return None

    module_path, class_name, desc = COLLECTORS[name]
    print(f"\n{'='*60}")
    print(f"  ▶️  {name}: {desc}")
    print(f"{'='*60}")

    start = time.time()
    try:
        module = importlib.import_module(module_path)
        collector_class = getattr(module, class_name)
        collector = collector_class()
        results = collector.run()
        elapsed = time.time() - start
        print(f"  ⏱️  Completed in {elapsed:.1f}s")
        return results
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        print(f"     Collector may need refactoring to use base.py")
        return None
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    parser = argparse.ArgumentParser(description="RGVL Collector Orchestrator")
    parser.add_argument("--list", action="store_true", help="List available collectors")
    parser.add_argument("--only", nargs="+", help="Run only these collectors")
    parser.add_argument("--skip", nargs="+", help="Skip these collectors")
    parser.add_argument("--dry-run", action="store_true", help="Show what would run without executing")
    args = parser.parse_args()

    if args.list:
        list_collectors()
        return

    print(f"\n{'='*60}")
    print(f"  🔨 RGVL Collector Orchestrator")
    print(f"     {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")

    # Determine which collectors to run
    if args.only:
        to_run = [n for n in args.only if n in COLLECTORS]
        skipped = [n for n in args.only if n not in COLLECTORS]
        if skipped:
            print(f"\n  ⚠️  Unknown collectors skipped: {skipped}")
    else:
        to_run = list(COLLECTORS.keys())

    if args.skip:
        to_run = [n for n in to_run if n not in args.skip]

    print(f"\n  📋 Running {len(to_run)} collectors: {', '.join(to_run)}")

    if args.dry_run:
        print("\n  🔍 Dry run — no collectors executed")
        return

    # Run collectors
    total_start = time.time()
    results_summary = {}

    for name in to_run:
        result = run_collector(name)
        results_summary[name] = result

    # Final summary
    elapsed = time.time() - total_start
    print(f"\n{'='*60}")
    print(f"  📊 Final Summary")
    print(f"{'='*60}")

    total_added = 0
    total_updated = 0
    total_errors = 0

    for name, result in results_summary.items():
        if result:
            total_added += result.get("added", 0)
            total_updated += result.get("updated", 0)
            total_errors += len(result.get("errors", []))
            status = "✅"
        else:
            status = "❌"
            total_errors += 1
        print(f"  {status} {name}")

    print(f"\n  📊 Added: {total_added} | Updated: {total_updated} | Errors: {total_errors}")
    print(f"  ⏱️  Total time: {elapsed:.1f}s")
    print(f"\n  ✅ Orchestrator complete!\n")


if __name__ == "__main__":
    main()
