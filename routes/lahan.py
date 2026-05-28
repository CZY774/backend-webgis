from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from geoalchemy2.shape import to_shape
from database import get_db
from models_rev import SDA
from slowapi import Limiter
from slowapi.util import get_remote_address
import json

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.get("/")
@limiter.limit("100/minute")
def get_all_lahan(request: Request, db: Session = Depends(get_db)):
    lahan_list = db.query(SDA).all()
    result = []
    for lahan in lahan_list:
        geom = to_shape(lahan.polygon)
        result.append(
            {
                "id_sda": lahan.id_sda,
                "polygon": json.dumps(geom.__geo_interface__),
                "jenis_lahan": lahan.jenis_lahan,
                "luas_ha": float(lahan.luas_ha),
            }
        )
    return result
