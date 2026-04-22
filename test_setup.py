#!/usr/bin/env python3
"""Test script to verify the application setup"""

import sys
import os

print("=== Testing SIG Desa Prawoto Setup ===\n")

# Test 1: Import dependencies
print("1. Testing Python dependencies...")
try:
    import fastapi
    import sqlalchemy
    import geoalchemy2
    import psycopg2
    import passlib
    import jose
    import shapely
    import openpyxl

    print("   ✓ All dependencies imported successfully")
except ImportError as e:
    print(f"   ❌ Missing dependency: {e}")
    sys.exit(1)

# Test 2: Check environment variables
print("\n2. Checking environment configuration...")
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv("DATABASE_URL")
secret_key = os.getenv("SECRET_KEY")

if not db_url:
    print("   ❌ DATABASE_URL not set in .env")
    sys.exit(1)

if "username:password" in db_url:
    print("   ⚠️  WARNING: DATABASE_URL still has placeholder credentials")
else:
    print("   ✓ DATABASE_URL configured")

if secret_key == "your-secret-key-change-this-in-production":
    print("   ⚠️  WARNING: SECRET_KEY is still default (change for production)")
else:
    print("   ✓ SECRET_KEY configured")

# Test 3: Check database connection
print("\n3. Testing database connection...")
try:
    from database import engine

    with engine.connect() as conn:
        result = conn.execute(sqlalchemy.text("SELECT version()"))
        version = result.fetchone()[0]
        print(f"   ✓ Connected to PostgreSQL")

        # Check PostGIS
        result = conn.execute(sqlalchemy.text("SELECT PostGIS_version()"))
        postgis_version = result.fetchone()[0]
        print(f"   ✓ PostGIS extension available: {postgis_version}")
except Exception as e:
    print(f"   ❌ Database connection failed: {e}")
    print("   Make sure PostgreSQL is running and credentials in .env are correct")
    sys.exit(1)

# Test 4: Check if tables exist
print("\n4. Checking database tables...")
try:
    from models import Base

    inspector = sqlalchemy.inspect(engine)
    tables = inspector.get_table_names()

    expected_tables = [
        "admin",
        "fasilitas",
        "umkm",
        "wisata",
        "foto_wisata",
        "sda",
        "rw",
        "kependudukan",
    ]
    missing_tables = [t for t in expected_tables if t not in tables]

    if missing_tables:
        print(f"   ⚠️  Missing tables: {', '.join(missing_tables)}")
        print("   Run: python import_data.py")
    else:
        print("   ✓ All tables exist")

        # Check data
        from database import SessionLocal

        db = SessionLocal()
        from models import Fasilitas, UMKM, Wisata, SDA, RW, Admin

        counts = {
            "Fasilitas": db.query(Fasilitas).count(),
            "UMKM": db.query(UMKM).count(),
            "Wisata": db.query(Wisata).count(),
            "SDA": db.query(SDA).count(),
            "RW": db.query(RW).count(),
            "Admin": db.query(Admin).count(),
        }

        print("\n   Data counts:")
        for table, count in counts.items():
            status = "✓" if count > 0 else "⚠️ "
            print(f"   {status} {table}: {count} records")

        db.close()

except Exception as e:
    print(f"   ❌ Error checking tables: {e}")

# Test 5: Check data files
print("\n5. Checking source data files...")
data_files = [
    "Fasilitas.xlsx",
    "UMKM.xlsx",
    "Wisata.xlsx",
    "Kependudukan.xlsx",
    "Sawah.geojson",
    "Kebun.geojson",
    "Ladang.geojson",
    "Pemukiman.geojson",
    "BatasRW.geojson",
]

missing = []
for file in data_files:
    if not os.path.exists(f"../{file}"):
        missing.append(file)

if missing:
    print(f"   ⚠️  Missing files: {', '.join(missing)}")
else:
    print("   ✓ All source data files present")

print("\n=== Test Complete ===")
print("\nTo run the application:")
print("  Backend:  uvicorn main:app --reload")
print("  Frontend: cd ../frontend && python3 -m http.server 3000")
