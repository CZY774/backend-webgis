from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.models import Fasilitas
from app.routes.auth import get_current_admin
from app.rate_limit import limiter
from app.utils import sanitize_input
from app.image_utils import compress_base64_image
from app.pagination import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, paginate_query

router = APIRouter()


class FasilitasCreate(BaseModel):
    latitude: float
    longitude: float
    nama: str
    jenis: str
    deskripsi: Optional[str] = None
    lokasi: Optional[str] = None
    jam_operasional: Optional[str] = None
    fasilitas_pendukung: Optional[str] = None
    foto_base64: Optional[str] = None


class FasilitasUpdate(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    nama: Optional[str] = None
    jenis: Optional[str] = None
    deskripsi: Optional[str] = None
    lokasi: Optional[str] = None
    jam_operasional: Optional[str] = None
    fasilitas_pendukung: Optional[str] = None
    foto_base64: Optional[str] = None


@router.get("/")
@limiter.limit("100/minute")
def get_all_fasilitas(
    request: Request,
    page: Optional[int] = Query(None, ge=1),
    limit: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
    db: Session = Depends(get_db),
):
    query = db.query(Fasilitas).order_by(Fasilitas.id_fasilitas)
    if page is None:
        return query.all()
    return paginate_query(query, page, limit)


@router.get("/{id}")
@limiter.limit("100/minute")
def get_fasilitas(request: Request, id: int, db: Session = Depends(get_db)):
    fasilitas = db.query(Fasilitas).filter(Fasilitas.id_fasilitas == id).first()
    if not fasilitas:
        raise HTTPException(status_code=404, detail="Fasilitas not found")
    return fasilitas


@router.post("/")
@limiter.limit("20/minute")
def create_fasilitas(
    request: Request,
    data: FasilitasCreate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    fasilitas = Fasilitas(
        latitude=data.latitude,
        longitude=data.longitude,
        nama=sanitize_input(data.nama),
        jenis=sanitize_input(data.jenis),
        deskripsi=sanitize_input(data.deskripsi) if data.deskripsi else None,
        lokasi=sanitize_input(data.lokasi) if data.lokasi else None,
        jam_operasional=sanitize_input(data.jam_operasional)
        if data.jam_operasional
        else None,
        fasilitas_pendukung=sanitize_input(data.fasilitas_pendukung)
        if data.fasilitas_pendukung
        else None,
        foto_base64=compress_base64_image(data.foto_base64)
        if data.foto_base64
        else None,
        created_by=admin.id_admin,
        updated_by=admin.id_admin,
    )
    db.add(fasilitas)
    db.commit()
    db.refresh(fasilitas)
    return fasilitas


@router.put("/{id}")
@limiter.limit("30/minute")
def update_fasilitas(
    request: Request,
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
    if data.deskripsi is not None:
        fasilitas.deskripsi = sanitize_input(data.deskripsi)
    if data.lokasi is not None:
        fasilitas.lokasi = sanitize_input(data.lokasi)
    if data.jam_operasional is not None:
        fasilitas.jam_operasional = sanitize_input(data.jam_operasional)
    if data.fasilitas_pendukung is not None:
        fasilitas.fasilitas_pendukung = sanitize_input(data.fasilitas_pendukung)
    if data.foto_base64 is not None:
        fasilitas.foto_base64 = (
            compress_base64_image(data.foto_base64) if data.foto_base64 else None
        )

    fasilitas.updated_by = admin.id_admin
    db.commit()
    db.refresh(fasilitas)
    return fasilitas


@router.delete("/{id}")
@limiter.limit("20/minute")
def delete_fasilitas(
    request: Request,
    id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    fasilitas = db.query(Fasilitas).filter(Fasilitas.id_fasilitas == id).first()
    if not fasilitas:
        raise HTTPException(status_code=404, detail="Fasilitas not found")

    db.delete(fasilitas)
    db.commit()
    return {"message": "Fasilitas deleted successfully"}
