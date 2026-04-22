# SIG Desa Prawoto - Complete Application

Sistem Informasi Geografis (GIS) untuk Desa Prawoto, Sukolilo, Pati.

## Features
- 🗺️ Interactive map with Leaflet.js
- 📍 5 map layers: Fasilitas, UMKM, Wisata, SDA, Kependudukan
- 🔍 Search and filter functionality
- 🛣️ Routing/navigation with OSRM
- 👤 Admin dashboard with full CRUD operations
- 🔐 JWT authentication
- 📊 PostgreSQL + PostGIS for spatial data

## Prerequisites
- Python 3.9+
- PostgreSQL 14+ with PostGIS extension
- Git

## Quick Start

### 1. Setup PostgreSQL Database
```bash
# Login to PostgreSQL
sudo -u postgres psql

# Create database
CREATE DATABASE sig_prawoto;

# Connect to database
\c sig_prawoto

# Enable PostGIS extension
CREATE EXTENSION postgis;

# Exit
\q
```

### 2. Setup Backend
```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
cd backend
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database credentials:
# DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/sig_prawoto

# Import initial data
python import_data.py

# Run backend server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will run at: http://localhost:8000
API Docs: http://localhost:8000/docs

### 3. Run Frontend
```bash
# In a new terminal
cd frontend
python3 -m http.server 3000
```

Frontend will run at: http://localhost:3000

## Default Admin Credentials
- **Username**: admin
- **Password**: admin123

⚠️ **Change this in production!**

## Project Structure
```
.
├── backend/
│   ├── main.py              # FastAPI application
│   ├── models.py            # SQLAlchemy models
│   ├── database.py          # Database connection
│   ├── import_data.py       # Data import script
│   ├── routes/              # API routes
│   │   ├── auth.py          # Authentication
│   │   ├── fasilitas.py     # Fasilitas CRUD
│   │   ├── umkm.py          # UMKM CRUD
│   │   ├── wisata.py        # Wisata CRUD
│   │   ├── sda.py           # SDA CRUD
│   │   └── kependudukan.py  # Kependudukan CRUD
│   ├── requirements.txt     # Python dependencies
│   └── .env                 # Environment variables
├── frontend/
│   ├── index.html           # Public map page
│   ├── admin.html           # Admin dashboard
│   ├── css/
│   │   └── style.css        # Styles
│   └── js/
│       ├── map.js           # Map functionality
│       └── admin.js         # Admin functionality
├── database_design.md       # Database documentation
├── Fasilitas.xlsx           # Source data
├── UMKM.xlsx                # Source data
├── Wisata.xlsx              # Source data
├── Sawah.geojson            # Source data
├── Kebun.geojson            # Source data
├── Ladang.geojson           # Source data
├── Pemukiman.geojson        # Source data
├── BatasRW.geojson          # Source data
├── Kependudukan.xlsx        # Source data
└── README.md                # This file
```

## API Endpoints

### Public Endpoints
- `GET /api/fasilitas` - Get all fasilitas
- `GET /api/umkm` - Get all UMKM
- `GET /api/wisata` - Get all wisata
- `GET /api/sda` - Get all SDA
- `GET /api/kependudukan` - Get all kependudukan with RW data

### Admin Endpoints (Requires Authentication)
- `POST /api/auth/login` - Admin login
- `POST /api/fasilitas` - Create fasilitas
- `PUT /api/fasilitas/{id}` - Update fasilitas
- `DELETE /api/fasilitas/{id}` - Delete fasilitas
- (Similar endpoints for umkm, wisata, sda, kependudukan)

## Tech Stack
- **Backend**: FastAPI + SQLAlchemy + GeoAlchemy2
- **Database**: PostgreSQL + PostGIS
- **Frontend**: HTML/CSS/Bootstrap 5 + Leaflet.js
- **Routing**: Leaflet Routing Machine + OSRM
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt (passlib)

## Deployment

### Option 1: Render.com (Recommended)
1. Create account at render.com
2. Create PostgreSQL database with PostGIS
3. Create Web Service from GitHub repo
4. Set environment variables
5. Deploy!

### Option 2: Railway.app
1. Create account at railway.app
2. Create new project from GitHub
3. Add PostgreSQL with PostGIS plugin
4. Set environment variables
5. Deploy!

### Option 3: VPS (DigitalOcean, AWS, etc.)
1. Setup Ubuntu server
2. Install PostgreSQL + PostGIS
3. Install Python 3.9+
4. Clone repository
5. Setup systemd service for FastAPI
6. Setup Nginx as reverse proxy
7. Configure SSL with Let's Encrypt

## Development

### Adding New Features
1. Create new model in `models.py`
2. Create new route in `backend/routes/`
3. Include router in `main.py`
4. Update frontend to consume new API

### Database Migrations
```bash
# After model changes, recreate tables
python -c "from database import engine; from models import Base; Base.metadata.drop_all(engine); Base.metadata.create_all(engine)"

# Re-import data
python import_data.py
```

## Troubleshooting

### Database Connection Error
- Check PostgreSQL is running: `sudo systemctl status postgresql`
- Verify credentials in `.env`
- Ensure PostGIS extension is installed

### Import Data Error
- Ensure all xlsx and geojson files are in project root
- Check file permissions
- Verify data format matches expected structure

### CORS Error
- Backend CORS is set to allow all origins for development
- For production, update `allow_origins` in `main.py`

## License
MIT

## Contributors
- Talitha (Geodesy Engineering Student)
- Amazon Q Developer
