#!/usr/bin/env python3
"""
RGVL Database Backup Script
Creates automatic backups of the SQLite database.
Can be run manually or via cron.

Usage:
    python backup.py                    # Creates backup in .backups/
    python backup.py --keep 7          # Keep only last 7 backups
    python backup.py --compress        # Compress with gzip
"""

import os
import shutil
import argparse
from pathlib import Path
from datetime import datetime
import gzip

# Configuration
# NOTE: backup.py lives at data/backup.py, so we need parent.parent to reach project root.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKUP_DIR = PROJECT_ROOT / 'data' / '.backups'
DB_FILE = PROJECT_ROOT / 'data' / 'rgvl.db'

# Alternative paths in case of restructure
ALT_DB_PATHS = [
    PROJECT_ROOT / 'data' / 'rgvl.db',
    PROJECT_ROOT / 'database' / 'rgvl.db',
    PROJECT_ROOT / 'rgvl.db',
]


def find_database():
    """Find the database file."""
    # Try main path first
    if DB_FILE.exists():
        return DB_FILE
    
    # Try alternative paths
    for path in ALT_DB_PATHS:
        if path.exists():
            return path
    
    return None


def get_backup_filename(timestamp: datetime = None) -> str:
    """Generate backup filename with timestamp."""
    if timestamp is None:
        timestamp = datetime.now()
    return f"rgvl_{timestamp.strftime('%Y%m%d_%H%M%S')}.db"


def create_backup(compress: bool = False, keep: int = None) -> Path:
    """Create a backup of the database."""
    
    # Find database
    db_path = find_database()
    if not db_path:
        print(f"❌ Database not found!")
        print(f"   Searched in:")
        print(f"   - {DB_FILE}")
        for path in ALT_DB_PATHS:
            print(f"   - {path}")
        raise FileNotFoundError("Database file not found")
    
    print(f"📂 Found database: {db_path}")
    
    # Ensure backup directory exists
    BACKUP_DIR.mkdir(exist_ok=True)
    
    # Generate filename
    timestamp = datetime.now()
    filename = get_backup_filename(timestamp)
    backup_path = BACKUP_DIR / filename
    
    # Copy database
    print(f"📦 Creating backup: {filename}")
    shutil.copy2(db_path, backup_path)
    
    # Compress if requested
    if compress:
        compressed = BACKUP_DIR / f"{filename}.gz"
        with open(backup_path, 'rb') as f_in:
            with gzip.open(compressed, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        # Remove uncompressed
        backup_path.unlink()
        backup_path = compressed
        print(f"   Compressed: {backup_path}")
    
    # Get file size
    size = backup_path.stat().st_size
    size_kb = size / 1024
    
    print(f"✅ Backup created: {backup_path} ({size_kb:.1f} KB)")
    
    # Cleanup old backups if requested
    if keep:
        cleanup_old_backups(keep)
    
    return backup_path


def cleanup_old_backups(keep: int):
    """Remove old backups, keeping only the most recent N."""
    # Find all backup files
    backups = sorted(BACKUP_DIR.glob('rgvl_*.db*'), key=lambda p: p.stat().st_mtime, reverse=True)
    
    if len(backups) <= keep:
        print(f"   No cleanup needed ({len(backups)} backups, keeping {keep})")
        return
    
    # Remove old backups
    to_remove = backups[keep:]
    for old in to_remove:
        old.unlink()
        print(f"   🗑️  Removed old backup: {old.name}")
    
    print(f"   ✅ Kept {keep} most recent backups")


def list_backups():
    """List all available backups."""
    backups = sorted(BACKUP_DIR.glob('rgvl_*.db*'), key=lambda p: p.stat().st_mtime, reverse=True)
    
    if not backups:
        print("No backups found!")
        return
    
    print("📂 Available backups:")
    print("-" * 50)
    
    for i, backup in enumerate(backups, 1):
        size_kb = backup.stat().st_size / 1024
        mtime = datetime.fromtimestamp(backup.stat().st_mtime)
        
        # Try to parse date from filename
        try:
            date_str = backup.name.replace('rgvl_', '').replace('.db', '').replace('.gz', '')
            date_str = f"{date_str[:8]} {date_str[9:13]}"
        except:
            date_str = mtime.strftime('%Y%m%d %H%M%S')
        
        print(f"  {i}. {date_str} - {size_kb:.1f} KB")


def restore_backup(backup_name: str = None):
    """Restore from a specific backup."""
    if backup_name:
        backup_path = BACKUP_DIR / backup_name
    else:
        # Get most recent
        backups = sorted(BACKUP_DIR.glob('rgvl_*.db*'), key=lambda p: p.stat().st_mtime, reverse=True)
        if not backups:
            print("No backups found!")
            return
        backup_path = backups[0]
    
    # Find destination
    db_path = find_database()
    if not db_path:
        # Use default location
        db_path = DB_FILE
    
    print(f"♻️  Restoring from: {backup_path}")
    print(f"   To: {db_path}")
    
    # Handle compression
    if str(backup_path).endswith('.gz'):
        with gzip.open(backup_path, 'rb') as f_in:
            with open(db_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
    else:
        shutil.copy2(backup_path, db_path)
    
    print(f"✅ Restore complete!")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='RGVL Database Backup')
    parser.add_argument('--compress', action='store_true', help='Compress backups with gzip')
    parser.add_argument('--keep', type=int, help='Number of backups to keep')
    parser.add_argument('--list', action='store_true', help='List available backups')
    parser.add_argument('--restore', type=str, help='Restore from backup file')
    
    args = parser.parse_args()
    
    if args.list:
        list_backups()
    elif args.restore:
        restore_backup(args.restore)
    else:
        create_backup(compress=args.compress, keep=args.keep)


if __name__ == '__main__':
    main()
