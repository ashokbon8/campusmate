"""Import the reviewed data pack into an existing database without deleting user data.

Run from backend: python ../scripts/import_jscoe.py
Use --refresh only after reviewing changes to the canonical knowledge JSON.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))

from app.database import SessionLocal, init_db
from app.services.college_data import seed_jscoe_data

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refresh', action='store_true')
    args = parser.parse_args()
    init_db()
    with SessionLocal() as db:
        print(seed_jscoe_data(db, refresh=args.refresh))
