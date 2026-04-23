from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database import engine
import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="SIG Desa Prawoto API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trust Railway proxy headers
from fastapi.middleware.trustedhost import TrustedHostMiddleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])


@app.get("/")
def root():
    return {"message": "SIG Desa Prawoto API", "status": "running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


# Import and include routes
from routes import auth, fasilitas, umkm, wisata, sda, kependudukan

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(fasilitas.router, prefix="/api/fasilitas", tags=["Fasilitas"])
app.include_router(umkm.router, prefix="/api/umkm", tags=["UMKM"])
app.include_router(wisata.router, prefix="/api/wisata", tags=["Wisata"])
app.include_router(sda.router, prefix="/api/sda", tags=["SDA"])
app.include_router(
    kependudukan.router, prefix="/api/kependudukan", tags=["Kependudukan"]
)
