from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.models import Wisata, FotoWisata
from app.routes.auth import get_current_admin
from app.rate_limit import limiter
from app.utils import sanitize_input
from app.image_utils import compress_base64_image

router = APIRouter()


class WisataCreate(BaseModel):
    latitude: float
    longitude: float
    nama: str
    jenis: str
    deskripsi: Optional[str] = None
    cagar_budaya: Optional[str] = None
    lokasi: Optional[str] = None
    tarif: Optional[str] = None
    fasilitas: Optional[str] = None
    foto_base64: Optional[str] = None


class WisataUpdate(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    nama: Optional[str] = None
    jenis: Optional[str] = None
    deskripsi: Optional[str] = None
    cagar_budaya: Optional[str] = None
    lokasi: Optional[str] = None
    tarif: Optional[str] = None
    fasilitas: Optional[str] = None
    foto_base64: Optional[str] = None


class FotoWisataUpload(BaseModel):
    id_wisata: int
    foto_base64: str


@router.get("/")
@limiter.limit("100/minute")
def get_all_wisata(request: Request, db: Session = Depends(get_db)):
    wisata_list = db.query(Wisata).all()
    result = []
    for w in wisata_list:
        # Get first photo if exists
        first_photo = (
            db.query(FotoWisata).filter(FotoWisata.id_wisata == w.id_wisata).first()
        )
        result.append(
            {
                "id_wisata": w.id_wisata,
                "nama": w.nama,
                "jenis": w.jenis,
                "deskripsi": w.deskripsi,
                "cagar_budaya": w.cagar_budaya,
                "lokasi": w.lokasi,
                "tarif": w.tarif,
                "fasilitas": w.fasilitas,
                "latitude": w.latitude,
                "longitude": w.longitude,
                "foto_base64": first_photo.foto_base64
                if first_photo
                else w.foto_base64,
                "created_at": w.created_at,
                "updated_at": w.updated_at,
            }
        )
    return result


@router.get("/{id}")
@limiter.limit("100/minute")
def get_wisata(request: Request, id: int, db: Session = Depends(get_db)):
    wisata = db.query(Wisata).filter(Wisata.id_wisata == id).first()
    if not wisata:
        raise HTTPException(status_code=404, detail="Wisata not found")
    return wisata


@router.post("/")
@limiter.limit("20/minute")
def create_wisata(
    request: Request,
    data: WisataCreate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    # Compress photo if provided
    foto_compressed = (
        compress_base64_image(data.foto_base64) if data.foto_base64 else None
    )

    wisata = Wisata(
        latitude=data.latitude,
        longitude=data.longitude,
        nama=sanitize_input(data.nama),
        jenis=sanitize_input(data.jenis),
        deskripsi=sanitize_input(data.deskripsi) if data.deskripsi else None,
        cagar_budaya=sanitize_input(data.cagar_budaya) if data.cagar_budaya else None,
        lokasi=sanitize_input(data.lokasi) if data.lokasi else None,
        tarif=sanitize_input(data.tarif) if data.tarif else None,
        fasilitas=sanitize_input(data.fasilitas) if data.fasilitas else None,
        foto_base64=foto_compressed,
        created_by=admin.id_admin,
        updated_by=admin.id_admin,
    )
    db.add(wisata)
    db.commit()
    db.refresh(wisata)
    return wisata


@router.put("/{id}")
@limiter.limit("30/minute")
def update_wisata(
    request: Request,
    id: int,
    data: WisataUpdate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    wisata = db.query(Wisata).filter(Wisata.id_wisata == id).first()
    if not wisata:
        raise HTTPException(status_code=404, detail="Wisata not found")

    if data.latitude is not None:
        wisata.latitude = data.latitude
    if data.longitude is not None:
        wisata.longitude = data.longitude
    if data.nama is not None:
        wisata.nama = sanitize_input(data.nama)
    if data.jenis is not None:
        wisata.jenis = sanitize_input(data.jenis)
    if data.deskripsi is not None:
        wisata.deskripsi = sanitize_input(data.deskripsi)
    if data.cagar_budaya is not None:
        wisata.cagar_budaya = sanitize_input(data.cagar_budaya)
    if data.lokasi is not None:
        wisata.lokasi = sanitize_input(data.lokasi)
    if data.tarif is not None:
        wisata.tarif = sanitize_input(data.tarif)
    if data.fasilitas is not None:
        wisata.fasilitas = sanitize_input(data.fasilitas)
    if data.foto_base64 is not None:
        wisata.foto_base64 = compress_base64_image(data.foto_base64)

    wisata.updated_by = admin.id_admin
    db.commit()
    db.refresh(wisata)
    return wisata


@router.delete("/{id}")
@limiter.limit("20/minute")
def delete_wisata(
    request: Request,
    id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    wisata = db.query(Wisata).filter(Wisata.id_wisata == id).first()
    if not wisata:
        raise HTTPException(status_code=404, detail="Wisata not found")

    db.delete(wisata)
    db.commit()
    return {"message": "Wisata deleted successfully"}


# Photo upload endpoints
@router.post("/photo/upload")
@limiter.limit("10/minute")
def upload_foto_wisata(
    request: Request,
    data: FotoWisataUpload,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    """Upload additional photo for wisata (max 15 photos per wisata)"""
    wisata = db.query(Wisata).filter(Wisata.id_wisata == data.id_wisata).first()
    if not wisata:
        raise HTTPException(status_code=404, detail="Wisata not found")

    # Check photo count limit
    photo_count = (
        db.query(FotoWisata).filter(FotoWisata.id_wisata == data.id_wisata).count()
    )
    if photo_count >= 15:
        raise HTTPException(status_code=400, detail="Maximum 15 photos per wisata")

    # Compress photo before saving
    foto_compressed = compress_base64_image(data.foto_base64)

    foto = FotoWisata(
        id_wisata=data.id_wisata,
        foto_base64=foto_compressed,
        uploaded_by=admin.id_admin,
    )
    db.add(foto)
    db.commit()
    db.refresh(foto)
    return {"message": "Photo uploaded successfully", "id_foto": foto.id_foto}


@router.get("/{id}/photos")
@limiter.limit("100/minute")
def get_wisata_photos(request: Request, id: int, db: Session = Depends(get_db)):
    """Get all photos for a wisata"""
    wisata = db.query(Wisata).filter(Wisata.id_wisata == id).first()
    if not wisata:
        raise HTTPException(status_code=404, detail="Wisata not found")

    photos = db.query(FotoWisata).filter(FotoWisata.id_wisata == id).all()
    return photos


@router.delete("/photo/{id_foto}")
@limiter.limit("20/minute")
def delete_foto_wisata(
    request: Request,
    id_foto: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    """Delete a photo"""
    foto = db.query(FotoWisata).filter(FotoWisata.id_foto == id_foto).first()
    if not foto:
        raise HTTPException(status_code=404, detail="Photo not found")

    db.delete(foto)
    db.commit()
    return {"message": "Photo deleted successfully"}
