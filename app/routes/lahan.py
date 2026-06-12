from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from geoalchemy2.shape import to_shape
from app.database import get_db
from app.models import SDA
from app.rate_limit import limiter
import json

router = APIRouter()


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
