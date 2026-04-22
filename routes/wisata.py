from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database import get_db
from models import Wisata
from routes.auth import get_current_admin

router = APIRouter()


class WisataCreate(BaseModel):
    latitude: float
    longitude: float
    nama: str
    jenis: str
    deskripsi: Optional[str] = None


class WisataUpdate(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    nama: Optional[str] = None
    jenis: Optional[str] = None
    deskripsi: Optional[str] = None


@router.get("/")
def get_all_wisata(db: Session = Depends(get_db)):
    return db.query(Wisata).all()


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
    wisata = Wisata(**data.dict())
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
