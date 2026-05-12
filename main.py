from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
import models_rev as models
import os
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

models.Base.metadata.create_all(bind=engine)

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="SIG Desa Prawoto API", version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS configuration with environment variable
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "SIG Desa Prawoto API", "status": "running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


# Import and include routes
from routes import (
    auth,
    fasilitas,
    umkm,
    wisata,
    sda,
    kependudukan,
    jalan,
    sungai,
    lahan,
)

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(fasilitas.router, prefix="/api/fasilitas", tags=["Fasilitas"])
app.include_router(umkm.router, prefix="/api/umkm", tags=["UMKM"])
app.include_router(wisata.router, prefix="/api/wisata", tags=["Wisata"])
app.include_router(sda.router, prefix="/api/sda", tags=["SDA"])
app.include_router(lahan.router, prefix="/api/lahan", tags=["Lahan"])
app.include_router(jalan.router, prefix="/api/jalan", tags=["Jalan"])
app.include_router(sungai.router, prefix="/api/sungai", tags=["Sungai"])
app.include_router(
    kependudukan.router, prefix="/api/kependudukan", tags=["Kependudukan"]
)
