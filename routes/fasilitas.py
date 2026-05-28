from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database import get_db
from models_rev import Fasilitas
from routes.auth import get_current_admin
from slowapi import Limiter
from slowapi.util import get_remote_address
from utils import sanitize_input

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


class FasilitasCreate(BaseModel):
    latitude: float
    longitude: float
    nama: str
    jenis: str


class FasilitasUpdate(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    nama: Optional[str] = None
    jenis: Optional[str] = None


@router.get("/")
@limiter.limit("100/minute")
def get_all_fasilitas(request: Request, db: Session = Depends(get_db)):
    return db.query(Fasilitas).all()


@router.get("/{id}")
@limiter.limit("100/minute")
def get_fasilitas(request: Request, id: int, db: Session = Depends(get_db)):
    fasilitas = db.query(Fasilitas).filter(Fasilitas.id_fasilitas == id).first()
    if not fasilitas:
        raise HTTPException(status_code=404, detail="Fasilitas not found")
    return fasilitas


@router.post("/")
def create_fasilitas(
    data: FasilitasCreate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    fasilitas = Fasilitas(
        latitude=data.latitude,
        longitude=data.longitude,
        nama=sanitize_input(data.nama),
        jenis=sanitize_input(data.jenis),
        created_by=admin.id_admin,
        updated_by=admin.id_admin,
    )
    db.add(fasilitas)
    db.commit()
    db.refresh(fasilitas)
    return fasilitas


@router.put("/{id}")
def update_fasilitas(
    id: int,
    data: FasilitasUpdate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    fasilitas = db.query(Fasilitas).filter(Fasilitas.id_fasilitas == id).first()
    if not fasilitas:
        raise HTTPException(status_code=404, detail="Fasilitas not found")

    if data.latitude is not None:
        fasilitas.latitude = data.latitude
    if data.longitude is not None:
        fasilitas.longitude = data.longitude
    if data.nama is not None:
        fasilitas.nama = sanitize_input(data.nama)
    if data.jenis is not None:
        fasilitas.jenis = sanitize_input(data.jenis)

    fasilitas.updated_by = admin.id_admin
    db.commit()
    db.refresh(fasilitas)
    return fasilitas


@router.delete("/{id}")
def delete_fasilitas(
    id: int, db: Session = Depends(get_db), admin=Depends(get_current_admin)
):
    fasilitas = db.query(Fasilitas).filter(Fasilitas.id_fasilitas == id).first()
    if not fasilitas:
        raise HTTPException(status_code=404, detail="Fasilitas not found")

    db.delete(fasilitas)
    db.commit()
    return {"message": "Fasilitas deleted successfully"}
