from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from geoalchemy2.shape import to_shape, from_shape
from shapely.geometry import shape
from database import get_db
from models import SDA
from routes.auth import get_current_admin
import json

router = APIRouter()


class SDACreate(BaseModel):
    polygon: dict
    jenis_lahan: str
    luas_ha: float


class SDAUpdate(BaseModel):
    polygon: Optional[dict] = None
    jenis_lahan: Optional[str] = None
    luas_ha: Optional[float] = None


@router.get("/")
def get_all_sda(db: Session = Depends(get_db)):
    sda_list = db.query(SDA).all()
    result = []
    for sda in sda_list:
        geom = to_shape(sda.polygon)
        result.append(
            {
                "id_sda": sda.id_sda,
                "polygon": json.dumps(geom.__geo_interface__),
                "jenis_lahan": sda.jenis_lahan,
                "luas_ha": float(sda.luas_ha),
                "created_at": sda.created_at,
                "updated_at": sda.updated_at,
            }
        )
    return result


@router.get("/{id}")
def get_sda(id: int, db: Session = Depends(get_db)):
    sda = db.query(SDA).filter(SDA.id_sda == id).first()
    if not sda:
        raise HTTPException(status_code=404, detail="SDA not found")

    geom = to_shape(sda.polygon)
    return {
        "id_sda": sda.id_sda,
        "polygon": json.dumps(geom.__geo_interface__),
        "jenis_lahan": sda.jenis_lahan,
        "luas_ha": float(sda.luas_ha),
        "created_at": sda.created_at,
        "updated_at": sda.updated_at,
    }


@router.post("/")
def create_sda(
    data: SDACreate, db: Session = Depends(get_db), admin=Depends(get_current_admin)
):
    geom = shape(data.polygon)
    sda = SDA(
        polygon=from_shape(geom, srid=4326),
        jenis_lahan=data.jenis_lahan,
        luas_ha=data.luas_ha,
    )
    db.add(sda)
    db.commit()
    db.refresh(sda)
    return {"message": "SDA created successfully", "id": sda.id_sda}


@router.put("/{id}")
def update_sda(
    id: int,
    data: SDAUpdate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    sda = db.query(SDA).filter(SDA.id_sda == id).first()
    if not sda:
        raise HTTPException(status_code=404, detail="SDA not found")

    if data.polygon:
        geom = shape(data.polygon)
        sda.polygon = from_shape(geom, srid=4326)
    if data.jenis_lahan:
        sda.jenis_lahan = data.jenis_lahan
    if data.luas_ha:
        sda.luas_ha = data.luas_ha

    db.commit()
    db.refresh(sda)
    return {"message": "SDA updated successfully"}


@router.delete("/{id}")
def delete_sda(
    id: int, db: Session = Depends(get_db), admin=Depends(get_current_admin)
):
    sda = db.query(SDA).filter(SDA.id_sda == id).first()
    if not sda:
        raise HTTPException(status_code=404, detail="SDA not found")

    db.delete(sda)
    db.commit()
    return {"message": "SDA deleted successfully"}
