from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from geoalchemy2.shape import to_shape
from database import get_db
from models import RW, Kependudukan
from routes.auth import get_current_admin
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
def get_all_kependudukan(db: Session = Depends(get_db)):
    result = []
    rw_list = db.query(RW).all()

    for rw in rw_list:
        kependudukan = (
            db.query(Kependudukan).filter(Kependudukan.id_rw == rw.id_rw).first()
        )
        geom = to_shape(rw.polygon)

        data = {
            "id_rw": rw.id_rw,
            "nomor_rw": rw.nomor_rw,
            "polygon": json.dumps(geom.__geo_interface__),
        }

        if kependudukan:
            data.update(
                {
                    "id_kependudukan": kependudukan.id_kependudukan,
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

    return result


@router.get("/{id}")
def get_kependudukan(id: int, db: Session = Depends(get_db)):
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
def update_kependudukan(
    id: int,
    data: KependudukanUpdate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    kependudukan = (
        db.query(Kependudukan).filter(Kependudukan.id_kependudukan == id).first()
    )
    if not kependudukan:
        raise HTTPException(status_code=404, detail="Kependudukan not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(kependudukan, key, value)

    db.commit()
    db.refresh(kependudukan)
    return {"message": "Kependudukan updated successfully"}
