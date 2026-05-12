from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from geoalchemy2.shape import to_shape
from database import get_db
from models_rev import Sungai
import json

router = APIRouter()


@router.get("/")
def get_all_sungai(db: Session = Depends(get_db)):
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
