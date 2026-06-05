from sqlalchemy import text

from database import engine
import models_rev as models


POINT_LAYER_COLUMNS = {
    "wisata": [
        ("cagar_budaya", "TEXT"),
        ("lokasi", "TEXT"),
        ("tarif", "VARCHAR(100)"),
        ("fasilitas", "TEXT"),
    ],
    "fasilitas": [
        ("deskripsi", "TEXT"),
        ("lokasi", "TEXT"),
        ("jam_operasional", "VARCHAR(100)"),
        ("fasilitas_pendukung", "TEXT"),
    ],
    "umkm": [
        ("pemilik", "VARCHAR(255)"),
        ("lokasi", "TEXT"),
        ("produk", "TEXT"),
        ("jam_operasional", "VARCHAR(100)"),
        ("fasilitas_pendukung", "TEXT"),
    ],
}


def ensure_data_fix_schema():
    models.Base.metadata.create_all(bind=engine)

    with engine.begin() as connection:
        for table_name, columns in POINT_LAYER_COLUMNS.items():
            for column_name, column_type in columns:
                connection.execute(
                    text(
                        f"ALTER TABLE {table_name} "
                        f"ADD COLUMN IF NOT EXISTS {column_name} {column_type}"
                    )
                )


def main():
    ensure_data_fix_schema()
    print("Data fix schema migration completed.")


if __name__ == "__main__":
    main()
