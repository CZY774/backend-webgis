from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from geoalchemy2.shape import to_shape
from app.database import get_db
from app.models import Sungai
from app.rate_limit import limiter
import json

router = APIRouter()


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
