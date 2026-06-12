import base64
import sys
from pathlib import Path

LEGACY_DIR = Path(__file__).resolve().parent
BACKEND_DIR = LEGACY_DIR.parent.parent
PROJECT_DIR = BACKEND_DIR.parent

backend_path = str(BACKEND_DIR)
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.image_utils import (
    TRUSTED_IMPORT_MAX_IMAGE_BYTES,
    compress_base64_image,
    get_image_size_kb,
)

# Photo directory
FOTO_DIR = PROJECT_DIR.parent / "foto wisata"

# Mapping of photo files to wisata names
WISATA_PHOTOS = {
    "Sendang Jibing.jpg": "Sendang Jibing",
    "Sendang Widodaren.jpg": "Sendang Widodaren",
    "Makam Sunan Prawoto.jpg": "Makam Mbah Sunan Prawoto",
    "Makam Mbah Tabek Merto Kamdowo.jpg": "Makam Mbah Tabek Merto Kamdowo",
    "Makam Wali Syekh Khalifah.jpg": "Makam Wali Syeh Khalifah",
}

PROFIL_DESA_PHOTO = "Gerbang Desa Prawoto.jpg"


def image_to_base64(image_path):
    """Convert image file to base64 string with data URI"""
    with open(image_path, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode("utf-8")
        # Determine MIME type
        ext = image_path.suffix.lower()
        if ext == ".webp":
            mime_type = "image/webp"
        elif ext == ".png":
            mime_type = "image/png"
        else:
            mime_type = "image/jpeg"
        return f"data:{mime_type};base64,{encoded}"


def main():
    from app.database import SessionLocal
    from app.models import Wisata, Desa, FotoWisata

    db = SessionLocal()

    try:
        # Upload wisata photos
        print("Uploading wisata photos...")
        for filename, wisata_name in WISATA_PHOTOS.items():
            photo_path = FOTO_DIR / filename
            if not photo_path.exists():
                print(f"  [!] Photo not found: {filename}")
                continue

            # Find wisata by name
            wisata = db.query(Wisata).filter(Wisata.nama == wisata_name).first()
            if not wisata:
                print(f"  [!] Wisata not found: {wisata_name}")
                continue

            # Convert to base64
            print(f"  Converting {filename}...")
            original_data = image_to_base64(photo_path)
            base64_data = compress_base64_image(
                original_data,
                max_input_bytes=TRUSTED_IMPORT_MAX_IMAGE_BYTES,
            )
            print(
                f"  Size: {get_image_size_kb(original_data):.1f} KB -> "
                f"{get_image_size_kb(base64_data):.1f} KB"
            )

            # Check if photo already exists
            existing_photo = (
                db.query(FotoWisata)
                .filter(FotoWisata.id_wisata == wisata.id_wisata)
                .first()
            )

            if existing_photo:
                # Update existing
                existing_photo.foto_base64 = base64_data
                print(f"  [OK] Updated photo for {wisata_name}")
            else:
                # Create new
                foto = FotoWisata(id_wisata=wisata.id_wisata, foto_base64=base64_data)
                db.add(foto)
                print(f"  [OK] Added photo for {wisata_name}")

        # Commit wisata photos first
        db.commit()
        print("\n[SUCCESS] Wisata photos uploaded!")

        # Upload profil desa photo
        print("\nUploading profil desa photo...")
        profil_photo_path = FOTO_DIR / PROFIL_DESA_PHOTO
        if profil_photo_path.exists():
            print(f"  Converting {PROFIL_DESA_PHOTO}...")
            original_data = image_to_base64(profil_photo_path)
            base64_data = compress_base64_image(
                original_data,
                max_input_bytes=TRUSTED_IMPORT_MAX_IMAGE_BYTES,
            )
            print(
                f"  Size: {get_image_size_kb(original_data):.1f} KB -> "
                f"{get_image_size_kb(base64_data):.1f} KB"
            )

            desa = db.query(Desa).first()
            if desa:
                desa.foto_base64 = base64_data
                db.commit()
                print(f"  [OK] Updated profil desa photo")
            else:
                print(f"  [!] Desa record not found")
        else:
            print(f"  [!] Photo not found: {PROFIL_DESA_PHOTO}")

        print("\n[SUCCESS] All photos uploaded successfully!")

    except Exception as e:
        print(f"\n[ERROR] {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
