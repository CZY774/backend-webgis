from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from geoalchemy2.shape import to_shape
from database import get_db
from models_rev import Jalan
from slowapi import Limiter
from slowapi.util import get_remote_address
import json

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.get("/")
@limiter.limit("100/minute")
def get_all_jalan(request: Request, db: Session = Depends(get_db)):
    jalan_list = db.query(Jalan).all()
    result = []
    for jalan in jalan_list:
        geom = to_shape(jalan.linestring)
        result.append(
            {
                "id_jalan": jalan.id_jalan,
                "geometry": json.dumps(geom.__geo_interface__),
                "nama_jalan": jalan.nama_jalan,
                "jenis": jalan.jenis,
                "permukaan": jalan.permukaan,
                "lebar_m": float(jalan.lebar_m) if jalan.lebar_m else None,
            }
        )
    return result
