from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database import get_db
from models_rev import UMKM
from routes.auth import get_current_admin
from slowapi import Limiter
from slowapi.util import get_remote_address
from utils import sanitize_input

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


class UMKMCreate(BaseModel):
    latitude: float
    longitude: float
    nama: str
    jenis: str


class UMKMUpdate(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    nama: Optional[str] = None
    jenis: Optional[str] = None


@router.get("/")
@limiter.limit("100/minute")
def get_all_umkm(request: Request, db: Session = Depends(get_db)):
    return db.query(UMKM).all()


@router.get("/{id}")
@limiter.limit("100/minute")
def get_umkm(request: Request, id: int, db: Session = Depends(get_db)):
    umkm = db.query(UMKM).filter(UMKM.id_umkm == id).first()
    if not umkm:
        raise HTTPException(status_code=404, detail="UMKM not found")
    return umkm


@router.post("/")
def create_umkm(
    data: UMKMCreate, db: Session = Depends(get_db), admin=Depends(get_current_admin)
):
    umkm = UMKM(
        latitude=data.latitude,
        longitude=data.longitude,
        nama=sanitize_input(data.nama),
        jenis=sanitize_input(data.jenis),
        created_by=admin.id_admin,
        updated_by=admin.id_admin,
    )
    db.add(umkm)
    db.commit()
    db.refresh(umkm)
    return umkm


@router.put("/{id}")
def update_umkm(
    id: int,
    data: UMKMUpdate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    umkm = db.query(UMKM).filter(UMKM.id_umkm == id).first()
    if not umkm:
        raise HTTPException(status_code=404, detail="UMKM not found")

    if data.latitude is not None:
        umkm.latitude = data.latitude
    if data.longitude is not None:
        umkm.longitude = data.longitude
    if data.nama is not None:
        umkm.nama = sanitize_input(data.nama)
    if data.jenis is not None:
        umkm.jenis = sanitize_input(data.jenis)

    umkm.updated_by = admin.id_admin
    db.commit()
    db.refresh(umkm)
    return umkm


@router.delete("/{id}")
def delete_umkm(
    id: int, db: Session = Depends(get_db), admin=Depends(get_current_admin)
):
    umkm = db.query(UMKM).filter(UMKM.id_umkm == id).first()
    if not umkm:
        raise HTTPException(status_code=404, detail="UMKM not found")

    db.delete(umkm)
    db.commit()
    return {"message": "UMKM deleted successfully"}
