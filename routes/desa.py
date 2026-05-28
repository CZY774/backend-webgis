from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from database import get_db
from slowapi import Limiter
from slowapi.util import get_remote_address
import models_rev as models

router = APIRouter(prefix="/api/desa", tags=["desa"])
limiter = Limiter(key_func=get_remote_address)


@router.get("/")
@limiter.limit("100/minute")
def get_desa(request: Request, db: Session = Depends(get_db)):
    desa = db.query(models.Desa).first()
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
    }
