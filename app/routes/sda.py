from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from geoalchemy2.shape import to_shape, from_shape
from shapely.geometry import shape
from app.database import get_db
from app.models import SDA
from app.routes.auth import get_current_admin
from app.rate_limit import limiter
from app.pagination import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, paginate_query
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
@limiter.limit("100/minute")
def get_all_sda(
    request: Request,
    page: Optional[int] = Query(None, ge=1),
    limit: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
    include_geometry: bool = Query(True),
    db: Session = Depends(get_db),
):
    query = db.query(SDA).order_by(SDA.id_sda)

    def serialize_sda(sda):
        data = {
            "id_sda": sda.id_sda,
            "jenis_lahan": sda.jenis_lahan,
            "luas_ha": float(sda.luas_ha),
            "created_at": sda.created_at,
            "updated_at": sda.updated_at,
        }
        if not include_geometry:
            return data

        geom = to_shape(sda.polygon)
        data["polygon"] = json.dumps(geom.__geo_interface__)
        return data

    if page is None:
        return [serialize_sda(sda) for sda in query.all()]
    return paginate_query(query, page, limit, serialize_sda)


@router.get("/{id}")
@limiter.limit("100/minute")
def get_sda(request: Request, id: int, db: Session = Depends(get_db)):
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
@limiter.limit("15/minute")
def create_sda(
    request: Request,
    data: SDACreate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    geom = shape(data.polygon)
    sda = SDA(
        polygon=from_shape(geom, srid=4326),
        jenis_lahan=data.jenis_lahan,
        luas_ha=data.luas_ha,
        created_by=admin.id_admin,
        updated_by=admin.id_admin,
    )
    db.add(sda)
    db.commit()
    db.refresh(sda)
    return {"message": "SDA created successfully", "id": sda.id_sda}


@router.put("/{id}")
@limiter.limit("20/minute")
def update_sda(
    request: Request,
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

    sda.updated_by = admin.id_admin
    db.commit()
    db.refresh(sda)
    return {"message": "SDA updated successfully"}


@router.delete("/{id}")
@limiter.limit("15/minute")
def delete_sda(
    request: Request,
    id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    sda = db.query(SDA).filter(SDA.id_sda == id).first()
    if not sda:
        raise HTTPException(status_code=404, detail="SDA not found")

    db.delete(sda)
    db.commit()
    return {"message": "SDA deleted successfully"}
