from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from geoalchemy2.shape import to_shape
from app.database import get_db
from app.models import RW, RT, Kependudukan, KependudukanRT
from app.routes.auth import get_current_admin
from app.rate_limit import limiter
from app.pagination import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
import json

router = APIRouter()


class KependudukanUpdate(BaseModel):
    jumlah_warga: Optional[int] = None
    laki_laki: Optional[int] = None
    perempuan: Optional[int] = None
    anak_anak: Optional[int] = None
    produktif: Optional[int] = None
    lansia: Optional[int] = None
    tidak_sekolah: Optional[int] = None
    tidak_tamat_sd: Optional[int] = None
    tamat_sd: Optional[int] = None
    sltp: Optional[int] = None
    slta: Optional[int] = None
    diploma_s1: Optional[int] = None
    belum_bekerja: Optional[int] = None
    pelajar: Optional[int] = None
    mengurus_rt: Optional[int] = None
    wiraswasta: Optional[int] = None
    petani: Optional[int] = None
    lainnya: Optional[int] = None


@router.get("/")
@limiter.limit("100/minute")
def get_all_kependudukan(
    request: Request,
    page: Optional[int] = Query(None, ge=1),
    limit: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
    include_geometry: bool = Query(True),
    db: Session = Depends(get_db),
):
    result = []
    rt_count = db.query(KependudukanRT).count()
    safe_page = max(page or 1, 1)
    safe_limit = min(max(limit, 1), MAX_PAGE_SIZE)

    if rt_count:
        query = db.query(RT).order_by(RT.id_rw, RT.nomor_rt)
        total = query.count()
        if page is not None:
            query = query.offset((safe_page - 1) * safe_limit).limit(safe_limit)

        rt_list = query.all()
        for rt in rt_list:
            kependudukan = (
                db.query(KependudukanRT)
                .filter(KependudukanRT.id_rt == rt.id_rt)
                .first()
            )

            rw = db.query(RW).filter(RW.id_rw == rt.id_rw).first()
            data = {
                "id_rt": rt.id_rt,
                "nomor_rt": rt.nomor_rt,
                "id_rw": rt.id_rw,
                "nomor_rw": rw.nomor_rw if rw else None,
            }
            if include_geometry:
                geom = to_shape(rt.polygon)
                data["polygon"] = json.dumps(geom.__geo_interface__)

            if kependudukan:
                data.update(kependudukan_to_dict(kependudukan))

            result.append(data)

        if page is not None:
            return {
                "items": result,
                "page": safe_page,
                "limit": safe_limit,
                "total": total,
                "total_pages": (total + safe_limit - 1) // safe_limit if total else 0,
            }

        return result

    query = db.query(RW).order_by(RW.id_rw)
    total = query.count()
    if page is not None:
        query = query.offset((safe_page - 1) * safe_limit).limit(safe_limit)

    rw_list = query.all()

    for rw in rw_list:
        kependudukan = (
            db.query(Kependudukan).filter(Kependudukan.id_rw == rw.id_rw).first()
        )

        data = {
            "id_rw": rw.id_rw,
            "nomor_rw": rw.nomor_rw,
        }
        if include_geometry:
            geom = to_shape(rw.polygon)
            data["polygon"] = json.dumps(geom.__geo_interface__)

        if kependudukan:
            data.update(
                {
                    "id_kependudukan": kependudukan.id_kependudukan,
                    "jumlah_kk": kependudukan.jumlah_kk,
                    "jumlah_warga": kependudukan.jumlah_warga,
                    "laki_laki": kependudukan.laki_laki,
                    "perempuan": kependudukan.perempuan,
                    "anak_anak": kependudukan.anak_anak,
                    "produktif": kependudukan.produktif,
                    "lansia": kependudukan.lansia,
                    "tidak_sekolah": kependudukan.tidak_sekolah,
                    "tidak_tamat_sd": kependudukan.tidak_tamat_sd,
                    "tamat_sd": kependudukan.tamat_sd,
                    "sltp": kependudukan.sltp,
                    "slta": kependudukan.slta,
                    "diploma_s1": kependudukan.diploma_s1,
                    "belum_bekerja": kependudukan.belum_bekerja,
                    "pelajar": kependudukan.pelajar,
                    "mengurus_rt": kependudukan.mengurus_rt,
                    "wiraswasta": kependudukan.wiraswasta,
                    "petani": kependudukan.petani,
                    "lainnya": kependudukan.lainnya,
                }
            )

        result.append(data)

    if page is not None:
        return {
            "items": result,
            "page": safe_page,
            "limit": safe_limit,
            "total": total,
            "total_pages": (total + safe_limit - 1) // safe_limit if total else 0,
        }

    return result


@router.get("/{id}")
@limiter.limit("100/minute")
def get_kependudukan(request: Request, id: int, db: Session = Depends(get_db)):
    kependudukan_rt = (
        db.query(KependudukanRT).filter(KependudukanRT.id_kependudukan_rt == id).first()
    )
    if kependudukan_rt:
        rt = db.query(RT).filter(RT.id_rt == kependudukan_rt.id_rt).first()
        rw = db.query(RW).filter(RW.id_rw == rt.id_rw).first() if rt else None
        geom = to_shape(rt.polygon)
        data = {
            "id_rt": rt.id_rt,
            "nomor_rt": rt.nomor_rt,
            "id_rw": rt.id_rw,
            "nomor_rw": rw.nomor_rw if rw else None,
            "polygon": json.dumps(geom.__geo_interface__),
        }
        data.update(kependudukan_to_dict(kependudukan_rt))
        return data

    kependudukan = (
        db.query(Kependudukan).filter(Kependudukan.id_kependudukan == id).first()
    )
    if not kependudukan:
        raise HTTPException(status_code=404, detail="Kependudukan not found")

    rw = db.query(RW).filter(RW.id_rw == kependudukan.id_rw).first()
    geom = to_shape(rw.polygon)

    return {
        "id_kependudukan": kependudukan.id_kependudukan,
        "id_rw": kependudukan.id_rw,
        "nomor_rw": rw.nomor_rw,
        "polygon": json.dumps(geom.__geo_interface__),
        "jumlah_warga": kependudukan.jumlah_warga,
        "laki_laki": kependudukan.laki_laki,
        "perempuan": kependudukan.perempuan,
        "anak_anak": kependudukan.anak_anak,
        "produktif": kependudukan.produktif,
        "lansia": kependudukan.lansia,
        "tidak_sekolah": kependudukan.tidak_sekolah,
        "tidak_tamat_sd": kependudukan.tidak_tamat_sd,
        "tamat_sd": kependudukan.tamat_sd,
        "sltp": kependudukan.sltp,
        "slta": kependudukan.slta,
        "diploma_s1": kependudukan.diploma_s1,
        "belum_bekerja": kependudukan.belum_bekerja,
        "pelajar": kependudukan.pelajar,
        "mengurus_rt": kependudukan.mengurus_rt,
        "wiraswasta": kependudukan.wiraswasta,
        "petani": kependudukan.petani,
        "lainnya": kependudukan.lainnya,
    }


@router.put("/{id}")
@limiter.limit("30/minute")
def update_kependudukan(
    request: Request,
    id: int,
    data: KependudukanUpdate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    kependudukan_rt = (
        db.query(KependudukanRT).filter(KependudukanRT.id_kependudukan_rt == id).first()
    )
    if kependudukan_rt:
        for key, value in data.dict(exclude_unset=True).items():
            setattr(kependudukan_rt, key, value)

        kependudukan_rt.updated_by = admin.id_admin
        db.commit()
        db.refresh(kependudukan_rt)
        return {"message": "Kependudukan RT updated successfully"}

    kependudukan = (
        db.query(Kependudukan).filter(Kependudukan.id_kependudukan == id).first()
    )
    if not kependudukan:
        raise HTTPException(status_code=404, detail="Kependudukan not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(kependudukan, key, value)

    kependudukan.updated_by = admin.id_admin
    db.commit()
    db.refresh(kependudukan)
    return {"message": "Kependudukan updated successfully"}


def kependudukan_to_dict(kependudukan):
    return {
        "id_kependudukan": kependudukan.id_kependudukan_rt,
        "id_kependudukan_rt": kependudukan.id_kependudukan_rt,
        "jumlah_kk": kependudukan.jumlah_kk,
        "jumlah_warga": kependudukan.jumlah_warga,
        "laki_laki": kependudukan.laki_laki,
        "perempuan": kependudukan.perempuan,
        "anak_anak": kependudukan.anak_anak,
        "produktif": kependudukan.produktif,
        "lansia": kependudukan.lansia,
        "tidak_sekolah": kependudukan.tidak_sekolah,
        "tidak_tamat_sd": kependudukan.tidak_tamat_sd,
        "tamat_sd": kependudukan.tamat_sd,
        "sltp": kependudukan.sltp,
        "slta": kependudukan.slta,
        "diploma_s1": kependudukan.diploma_s1,
        "belum_bekerja": kependudukan.belum_bekerja,
        "pelajar": kependudukan.pelajar,
        "mengurus_rt": kependudukan.mengurus_rt,
        "wiraswasta": kependudukan.wiraswasta,
        "petani": kependudukan.petani,
        "lainnya": kependudukan.lainnya,
    }
