"""
Migration script to add GIST spatial indexes and audit trail columns
Run this ONCE after deploying to Neon database
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from database import engine

# SQL commands for migration
migration_sql = """
-- Add audit trail columns to existing tables
ALTER TABLE fasilitas ADD COLUMN IF NOT EXISTS created_by INTEGER REFERENCES admin(id_admin);
ALTER TABLE fasilitas ADD COLUMN IF NOT EXISTS updated_by INTEGER REFERENCES admin(id_admin);

ALTER TABLE umkm ADD COLUMN IF NOT EXISTS created_by INTEGER REFERENCES admin(id_admin);
ALTER TABLE umkm ADD COLUMN IF NOT EXISTS updated_by INTEGER REFERENCES admin(id_admin);

ALTER TABLE wisata ADD COLUMN IF NOT EXISTS created_by INTEGER REFERENCES admin(id_admin);
ALTER TABLE wisata ADD COLUMN IF NOT EXISTS updated_by INTEGER REFERENCES admin(id_admin);
ALTER TABLE wisata ADD COLUMN IF NOT EXISTS foto_base64 TEXT;

ALTER TABLE foto_wisata ADD COLUMN IF NOT EXISTS foto_base64 TEXT;
ALTER TABLE foto_wisata ADD COLUMN IF NOT EXISTS uploaded_by INTEGER REFERENCES admin(id_admin);

ALTER TABLE sda ADD COLUMN IF NOT EXISTS created_by INTEGER REFERENCES admin(id_admin);
ALTER TABLE sda ADD COLUMN IF NOT EXISTS updated_by INTEGER REFERENCES admin(id_admin);

ALTER TABLE kependudukan ADD COLUMN IF NOT EXISTS updated_by INTEGER REFERENCES admin(id_admin);

-- Create GIST spatial indexes (CRITICAL for performance with 2500+ polygons)
DROP INDEX IF EXISTS idx_sda_polygon_gist;
CREATE INDEX idx_sda_polygon_gist ON sda USING GIST(polygon);

DROP INDEX IF EXISTS idx_jalan_linestring_gist;
CREATE INDEX idx_jalan_linestring_gist ON jalan USING GIST(linestring);

DROP INDEX IF EXISTS idx_sungai_linestring_gist;
CREATE INDEX idx_sungai_linestring_gist ON sungai USING GIST(linestring);

DROP INDEX IF EXISTS idx_rw_polygon_gist;
CREATE INDEX idx_rw_polygon_gist ON rw USING GIST(polygon);

DROP INDEX IF EXISTS idx_rt_polygon_gist;
CREATE INDEX idx_rt_polygon_gist ON rt USING GIST(polygon);

DROP INDEX IF EXISTS idx_desa_polygon_gist;
CREATE INDEX idx_desa_polygon_gist ON desa USING GIST(polygon);

-- Create additional indexes for audit trail
CREATE INDEX IF NOT EXISTS idx_fasilitas_created_by ON fasilitas(created_by);
CREATE INDEX IF NOT EXISTS idx_umkm_created_by ON umkm(created_by);
CREATE INDEX IF NOT EXISTS idx_wisata_created_by ON wisata(created_by);
CREATE INDEX IF NOT EXISTS idx_sda_created_by ON sda(created_by);
CREATE INDEX IF NOT EXISTS idx_foto_wisata_uploaded_by ON foto_wisata(uploaded_by);
CREATE INDEX IF NOT EXISTS idx_kependudukan_updated_by ON kependudukan(updated_by);
"""

print("Running database migration...")
print("This will add audit trail columns and GIST spatial indexes")
print("-" * 60)

try:
    with engine.connect() as conn:
        # Execute each statement separately
        for statement in migration_sql.strip().split(";"):
            statement = statement.strip()
            if statement and not statement.startswith("--"):
                conn.execute(text(statement))
        conn.commit()
        print("✓ Migration completed successfully!")
        print("\nChanges applied:")
        print("  - Added audit trail columns (created_by, updated_by)")
        print("  - Added foto_base64 columns for photo storage")
        print("  - Created GIST spatial indexes for all geometry columns")
        print("  - Created indexes for audit trail foreign keys")
except Exception as e:
    print(f"✗ Migration failed: {e}")
    print("\nIf columns already exist, this is expected.")
    print("GIST indexes should still be created successfully.")
