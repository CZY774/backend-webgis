from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
import models_rev as models

router = APIRouter(prefix="/api/desa", tags=["desa"])

@router.get("/")
def get_desa(db: Session = Depends(get_db)):
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
        "foto_base64": desa.foto_base64
    }
