from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.models import UMKM
from app.routes.auth import get_current_admin
from app.rate_limit import limiter
from app.utils import sanitize_input
from app.image_utils import compress_base64_image
from app.pagination import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, paginate_query

router = APIRouter()


class UMKMCreate(BaseModel):
    latitude: float
    longitude: float
    nama: str
    jenis: str
    pemilik: Optional[str] = None
    lokasi: Optional[str] = None
    produk: Optional[str] = None
    jam_operasional: Optional[str] = None
    fasilitas_pendukung: Optional[str] = None
    foto_base64: Optional[str] = None


class UMKMUpdate(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    nama: Optional[str] = None
    jenis: Optional[str] = None
    pemilik: Optional[str] = None
    lokasi: Optional[str] = None
    produk: Optional[str] = None
    jam_operasional: Optional[str] = None
    fasilitas_pendukung: Optional[str] = None
    foto_base64: Optional[str] = None


@router.get("/")
@limiter.limit("100/minute")
def get_all_umkm(
    request: Request,
    page: Optional[int] = Query(None, ge=1),
    limit: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
    db: Session = Depends(get_db),
):
    query = db.query(UMKM).order_by(UMKM.id_umkm)
    if page is None:
        return query.all()
    return paginate_query(query, page, limit)


@router.get("/{id}")
@limiter.limit("100/minute")
def get_umkm(request: Request, id: int, db: Session = Depends(get_db)):
    umkm = db.query(UMKM).filter(UMKM.id_umkm == id).first()
    if not umkm:
        raise HTTPException(status_code=404, detail="UMKM not found")
    return umkm


@router.post("/")
@limiter.limit("20/minute")
def create_umkm(
    request: Request,
    data: UMKMCreate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    umkm = UMKM(
        latitude=data.latitude,
        longitude=data.longitude,
        nama=sanitize_input(data.nama),
        jenis=sanitize_input(data.jenis),
        pemilik=sanitize_input(data.pemilik) if data.pemilik else None,
        lokasi=sanitize_input(data.lokasi) if data.lokasi else None,
        produk=sanitize_input(data.produk) if data.produk else None,
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
    db.add(umkm)
    db.commit()
    db.refresh(umkm)
    return umkm


@router.put("/{id}")
@limiter.limit("30/minute")
def update_umkm(
    request: Request,
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
    if data.pemilik is not None:
        umkm.pemilik = sanitize_input(data.pemilik)
    if data.lokasi is not None:
        umkm.lokasi = sanitize_input(data.lokasi)
    if data.produk is not None:
        umkm.produk = sanitize_input(data.produk)
    if data.jam_operasional is not None:
        umkm.jam_operasional = sanitize_input(data.jam_operasional)
    if data.fasilitas_pendukung is not None:
        umkm.fasilitas_pendukung = sanitize_input(data.fasilitas_pendukung)
    if data.foto_base64 is not None:
        umkm.foto_base64 = (
            compress_base64_image(data.foto_base64) if data.foto_base64 else None
        )

    umkm.updated_by = admin.id_admin
    db.commit()
    db.refresh(umkm)
    return umkm


@router.delete("/{id}")
@limiter.limit("20/minute")
def delete_umkm(
    request: Request,
    id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    umkm = db.query(UMKM).filter(UMKM.id_umkm == id).first()
    if not umkm:
        raise HTTPException(status_code=404, detail="UMKM not found")

    db.delete(umkm)
    db.commit()
    return {"message": "UMKM deleted successfully"}
