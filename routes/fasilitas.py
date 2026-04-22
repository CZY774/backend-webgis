from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database import get_db
from models import Fasilitas
from routes.auth import get_current_admin

router = APIRouter()


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
def get_all_fasilitas(db: Session = Depends(get_db)):
    return db.query(Fasilitas).all()


@router.get("/{id}")
def get_fasilitas(id: int, db: Session = Depends(get_db)):
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
    fasilitas = Fasilitas(**data.dict())
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

    for key, value in data.dict(exclude_unset=True).items():
        setattr(fasilitas, key, value)

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
