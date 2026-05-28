from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
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


# Security Headers Middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://unpkg.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' https://unpkg.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; img-src 'self' data: https: http:; font-src 'self' data: https://cdnjs.cloudflare.com;"
        )
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        return response


app.add_middleware(SecurityHeadersMiddleware)

# CORS configuration with environment variable
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
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
    desa,
)

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(fasilitas.router, prefix="/api/fasilitas", tags=["Fasilitas"])
app.include_router(umkm.router, prefix="/api/umkm", tags=["UMKM"])
app.include_router(wisata.router, prefix="/api/wisata", tags=["Wisata"])
app.include_router(sda.router, prefix="/api/sda", tags=["SDA"])
app.include_router(lahan.router, prefix="/api/lahan", tags=["Lahan"])
app.include_router(jalan.router, prefix="/api/jalan", tags=["Jalan"])
app.include_router(sungai.router, prefix="/api/sungai", tags=["Sungai"])
app.include_router(desa.router)
app.include_router(
    kependudukan.router, prefix="/api/kependudukan", tags=["Kependudukan"]
)
