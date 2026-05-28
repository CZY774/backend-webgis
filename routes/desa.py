from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from database import get_db
from models_rev import Desa
from geoalchemy2.functions import ST_AsGeoJSON
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.get("/")
@limiter.limit("100/minute")
def get_desa(request: Request, db: Session = Depends(get_db)):
    """Get desa boundary"""
    desa = db.query(
        Desa.id_desa,
        Desa.nama_desa,
        Desa.kecamatan,
        Desa.kabupaten,
        Desa.provinsi,
        Desa.luas_ha,
        Desa.foto_base64,
        ST_AsGeoJSON(Desa.polygon).label("geometry"),
    ).first()

    if not desa:
        return {}

    return {
        "id_desa": desa.id_desa,
        "nama_desa": desa.nama_desa,
        "kecamatan": desa.kecamatan,
        "kabupaten": desa.kabupaten,
        "provinsi": desa.provinsi,
        "luas_ha": desa.luas_ha,
        "foto_base64": desa.foto_base64,
        "geometry": desa.geometry,
    }
