from sqlalchemy import Column, Integer, String, DECIMAL, Text, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
from database import Base


class Admin(Base):
    __tablename__ = "admin"
    id_admin = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    last_login = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())


class Fasilitas(Base):
    __tablename__ = "fasilitas"
    id_fasilitas = Column(Integer, primary_key=True, index=True)
    latitude = Column(DECIMAL(10, 8), nullable=False)
    longitude = Column(DECIMAL(11, 8), nullable=False)
    nama = Column(String(255), nullable=False)
    jenis = Column(String(100), nullable=False, index=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


class UMKM(Base):
    __tablename__ = "umkm"
    id_umkm = Column(Integer, primary_key=True, index=True)
    latitude = Column(DECIMAL(10, 8), nullable=False)
    longitude = Column(DECIMAL(11, 8), nullable=False)
    nama = Column(String(255), nullable=False)
    jenis = Column(String(100), nullable=False, index=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


class Wisata(Base):
    __tablename__ = "wisata"
    id_wisata = Column(Integer, primary_key=True, index=True)
    latitude = Column(DECIMAL(10, 8), nullable=False)
    longitude = Column(DECIMAL(11, 8), nullable=False)
    nama = Column(String(255), nullable=False)
    jenis = Column(String(100), nullable=False, index=True)
    deskripsi = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


class FotoWisata(Base):
    __tablename__ = "foto_wisata"
    id_foto = Column(Integer, primary_key=True, index=True)
    id_wisata = Column(
        Integer,
        ForeignKey("wisata.id_wisata", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    file_path = Column(String(500), nullable=False)
    uploaded_at = Column(TIMESTAMP, server_default=func.now())


class SDA(Base):
    __tablename__ = "sda"
    id_sda = Column(Integer, primary_key=True, index=True)
    polygon = Column(Geometry(geometry_type="MULTIPOLYGON", srid=4326), nullable=False)
    jenis_lahan = Column(String(50), nullable=False, index=True)
    luas_ha = Column(DECIMAL(10, 4), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


class RW(Base):
    __tablename__ = "rw"
    id_rw = Column(Integer, primary_key=True, index=True)
    nomor_rw = Column(Integer, unique=True, nullable=False)
    polygon = Column(Geometry(geometry_type="MULTIPOLYGON", srid=4326), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


class Kependudukan(Base):
    __tablename__ = "kependudukan"
    id_kependudukan = Column(Integer, primary_key=True, index=True)
    id_rw = Column(
        Integer, ForeignKey("rw.id_rw", ondelete="CASCADE"), unique=True, nullable=False
    )
    jumlah_warga = Column(Integer, nullable=False)
    laki_laki = Column(Integer, nullable=False)
    perempuan = Column(Integer, nullable=False)
    anak_anak = Column(Integer, nullable=False)
    produktif = Column(Integer, nullable=False)
    lansia = Column(Integer, nullable=False)
    tidak_sekolah = Column(Integer, nullable=False)
    tidak_tamat_sd = Column(Integer, nullable=False)
    tamat_sd = Column(Integer, nullable=False)
    sltp = Column(Integer, nullable=False)
    slta = Column(Integer, nullable=False)
    diploma_s1 = Column(Integer, nullable=False)
    belum_bekerja = Column(Integer, nullable=False)
    pelajar = Column(Integer, nullable=False)
    mengurus_rt = Column(Integer, nullable=False)
    wiraswasta = Column(Integer, nullable=False)
    petani = Column(Integer, nullable=False)
    lainnya = Column(Integer, nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
