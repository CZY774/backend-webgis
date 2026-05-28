from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from geoalchemy2.shape import to_shape
from database import get_db
from models_rev import Sungai
from slowapi import Limiter
from slowapi.util import get_remote_address
import json

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.get("/")
@limiter.limit("100/minute")
def get_all_sungai(request: Request, db: Session = Depends(get_db)):
    sungai_list = db.query(Sungai).all()
    result = []
    for sungai in sungai_list:
        geom = to_shape(sungai.linestring)
        result.append(
            {
                "id_sungai": sungai.id_sungai,
                "geometry": json.dumps(geom.__geo_interface__),
                "nama_sungai": sungai.nama_sungai,
            }
        )
    return result
