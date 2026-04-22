from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database import get_db
from models import UMKM
from routes.auth import get_current_admin

router = APIRouter()


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
def get_all_umkm(db: Session = Depends(get_db)):
    return db.query(UMKM).all()


@router.get("/{id}")
def get_umkm(id: int, db: Session = Depends(get_db)):
    umkm = db.query(UMKM).filter(UMKM.id_umkm == id).first()
    if not umkm:
        raise HTTPException(status_code=404, detail="UMKM not found")
    return umkm


@router.post("/")
def create_umkm(
    data: UMKMCreate, db: Session = Depends(get_db), admin=Depends(get_current_admin)
):
    umkm = UMKM(**data.dict())
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

    for key, value in data.dict(exclude_unset=True).items():
        setattr(umkm, key, value)

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
