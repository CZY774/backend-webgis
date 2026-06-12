from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from app.database import engine
import app.models as models
import os
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.schema import ensure_data_fix_schema
from app.rate_limit import limiter

models.Base.metadata.create_all(bind=engine)
ensure_data_fix_schema()

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
            "default-src 'self'; "
            "base-uri 'self'; "
            "object-src 'none'; "
            "frame-ancestors 'none'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://unpkg.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://unpkg.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "img-src 'self' data: https: http:; "
            "font-src 'self' data: https://cdnjs.cloudflare.com; "
            "connect-src 'self' https: http://localhost:8000 http://127.0.0.1:8000;"
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
@limiter.limit("60/minute")
def root(request: Request):
    return {"message": "SIG Desa Prawoto API", "status": "running"}


@app.get("/health")
@limiter.limit("60/minute")
def health(request: Request):
    return {"status": "healthy"}


# Import and include routes
from app.routes import (
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
app.include_router(desa.router, prefix="/api/desa", tags=["Desa"])
app.include_router(
    kependudukan.router, prefix="/api/kependudukan", tags=["Kependudukan"]
)
