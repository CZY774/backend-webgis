from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database import get_db
from models_rev import Wisata, FotoWisata
from routes.auth import get_current_admin

router = APIRouter()


class WisataCreate(BaseModel):
    latitude: float
    longitude: float
    nama: str
    jenis: str
    deskripsi: Optional[str] = None
    foto_base64: Optional[str] = None


class WisataUpdate(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    nama: Optional[str] = None
    jenis: Optional[str] = None
    deskripsi: Optional[str] = None
    foto_base64: Optional[str] = None


class FotoWisataUpload(BaseModel):
    id_wisata: int
    foto_base64: str


@router.get("/")
def get_all_wisata(db: Session = Depends(get_db)):
    wisata_list = db.query(Wisata).all()
    result = []
    for w in wisata_list:
        # Get first photo if exists
        first_photo = db.query(FotoWisata).filter(FotoWisata.id_wisata == w.id_wisata).first()
        result.append({
            "id_wisata": w.id_wisata,
            "nama": w.nama,
            "jenis": w.jenis,
            "deskripsi": w.deskripsi,
            "latitude": w.latitude,
            "longitude": w.longitude,
            "foto_base64": first_photo.foto_base64 if first_photo else w.foto_base64,
            "created_at": w.created_at,
            "updated_at": w.updated_at
        })
    return result


@router.get("/{id}")
def get_wisata(id: int, db: Session = Depends(get_db)):
    wisata = db.query(Wisata).filter(Wisata.id_wisata == id).first()
    if not wisata:
        raise HTTPException(status_code=404, detail="Wisata not found")
    return wisata


@router.post("/")
def create_wisata(
    data: WisataCreate, db: Session = Depends(get_db), admin=Depends(get_current_admin)
):
    wisata = Wisata(**data.dict(), created_by=admin.id_admin, updated_by=admin.id_admin)
    db.add(wisata)
    db.commit()
    db.refresh(wisata)
    return wisata


@router.put("/{id}")
def update_wisata(
    id: int,
    data: WisataUpdate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    wisata = db.query(Wisata).filter(Wisata.id_wisata == id).first()
    if not wisata:
        raise HTTPException(status_code=404, detail="Wisata not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(wisata, key, value)

    wisata.updated_by = admin.id_admin
    db.commit()
    db.refresh(wisata)
    return wisata


@router.delete("/{id}")
def delete_wisata(
    id: int, db: Session = Depends(get_db), admin=Depends(get_current_admin)
):
    wisata = db.query(Wisata).filter(Wisata.id_wisata == id).first()
    if not wisata:
        raise HTTPException(status_code=404, detail="Wisata not found")

    db.delete(wisata)
    db.commit()
    return {"message": "Wisata deleted successfully"}


# Photo upload endpoints
@router.post("/photo/upload")
def upload_foto_wisata(
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

    foto = FotoWisata(
        id_wisata=data.id_wisata,
        foto_base64=data.foto_base64,
        uploaded_by=admin.id_admin,
    )
    db.add(foto)
    db.commit()
    db.refresh(foto)
    return {"message": "Photo uploaded successfully", "id_foto": foto.id_foto}


@router.get("/{id}/photos")
def get_wisata_photos(id: int, db: Session = Depends(get_db)):
    """Get all photos for a wisata"""
    wisata = db.query(Wisata).filter(Wisata.id_wisata == id).first()
    if not wisata:
        raise HTTPException(status_code=404, detail="Wisata not found")

    photos = db.query(FotoWisata).filter(FotoWisata.id_wisata == id).all()
    return photos


@router.delete("/photo/{id_foto}")
def delete_foto_wisata(
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
