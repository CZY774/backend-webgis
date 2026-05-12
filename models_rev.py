from sqlalchemy import Column, Integer, String, DECIMAL, Text, TIMESTAMP, ForeignKey, Float
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
from database import Base


class Admin(Base):
    __tablename__ = "admin"
    __table_args__ = {'extend_existing': True}
    id_admin = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    last_login = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())


class Fasilitas(Base):
    __tablename__ = "fasilitas"
    __table_args__ = {'extend_existing': True}
    id_fasilitas = Column(Integer, primary_key=True, index=True)
    latitude = Column(DECIMAL(10, 8), nullable=False)
    longitude = Column(DECIMAL(11, 8), nullable=False)
    nama = Column(String(255), nullable=False)
    jenis = Column(String(100), nullable=False, index=True)
    created_by = Column(Integer, ForeignKey("admin.id_admin"), nullable=True)
    updated_by = Column(Integer, ForeignKey("admin.id_admin"), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


class UMKM(Base):
    __tablename__ = "umkm"
    __table_args__ = {'extend_existing': True}
    id_umkm = Column(Integer, primary_key=True, index=True)
    latitude = Column(DECIMAL(10, 8), nullable=False)
    longitude = Column(DECIMAL(11, 8), nullable=False)
    nama = Column(String(255), nullable=False)
    jenis = Column(String(100), nullable=False, index=True)
    created_by = Column(Integer, ForeignKey("admin.id_admin"), nullable=True)
    updated_by = Column(Integer, ForeignKey("admin.id_admin"), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


class Wisata(Base):
    __tablename__ = "wisata"
    __table_args__ = {'extend_existing': True}
    id_wisata = Column(Integer, primary_key=True, index=True)
    latitude = Column(DECIMAL(10, 8), nullable=False)
    longitude = Column(DECIMAL(11, 8), nullable=False)
    nama = Column(String(255), nullable=False)
    jenis = Column(String(100), nullable=False, index=True)
    deskripsi = Column(Text, nullable=True)
    foto_base64 = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("admin.id_admin"), nullable=True)
    updated_by = Column(Integer, ForeignKey("admin.id_admin"), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


class FotoWisata(Base):
    __tablename__ = "foto_wisata"
    __table_args__ = {'extend_existing': True}
    id_foto = Column(Integer, primary_key=True, index=True)
    id_wisata = Column(
        Integer,
        ForeignKey("wisata.id_wisata", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    foto_base64 = Column(Text, nullable=False)
    uploaded_by = Column(Integer, ForeignKey("admin.id_admin"), nullable=True)
    uploaded_at = Column(TIMESTAMP, server_default=func.now())


class SDA(Base):
    __tablename__ = "sda"
    __table_args__ = {'extend_existing': True}
    id_sda = Column(Integer, primary_key=True, index=True)
    polygon = Column(Geometry(geometry_type="MULTIPOLYGON", srid=4326), nullable=False)
    jenis_lahan = Column(String(100), nullable=False, index=True)
    luas_ha = Column(DECIMAL(10, 4), nullable=False)
    created_by = Column(Integer, ForeignKey("admin.id_admin"), nullable=True)
    updated_by = Column(Integer, ForeignKey("admin.id_admin"), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


class RW(Base):
    __tablename__ = "rw"
    __table_args__ = {'extend_existing': True}
    id_rw = Column(Integer, primary_key=True, index=True)
    nomor_rw = Column(Integer, unique=True, nullable=False)
    polygon = Column(Geometry(geometry_type="MULTIPOLYGON", srid=4326), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


class Kependudukan(Base):
    __tablename__ = "kependudukan"
    __table_args__ = {'extend_existing': True}
    id_kependudukan = Column(Integer, primary_key=True, index=True)
    id_rw = Column(
        Integer, ForeignKey("rw.id_rw", ondelete="CASCADE"), unique=True, nullable=False
    )
    jumlah_kk = Column(Integer, nullable=True)
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
    updated_by = Column(Integer, ForeignKey("admin.id_admin"), nullable=True)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


# New models for additional geographic features

class Jalan(Base):
    __tablename__ = "jalan"
    __table_args__ = {'extend_existing': True}
    id_jalan = Column(Integer, primary_key=True, index=True)
    linestring = Column(Geometry(geometry_type="MULTILINESTRING", srid=4326), nullable=False)
    nama_jalan = Column(String(255), nullable=True)
    jenis = Column(String(50), nullable=True, index=True)
    permukaan = Column(String(50), nullable=True)
    lebar_m = Column(Float, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


class Sungai(Base):
    __tablename__ = "sungai"
    __table_args__ = {'extend_existing': True}
    id_sungai = Column(Integer, primary_key=True, index=True)
    linestring = Column(Geometry(geometry_type="MULTILINESTRING", srid=4326), nullable=False)
    nama_sungai = Column(String, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


class RT(Base):
    __tablename__ = "rt"
    __table_args__ = {'extend_existing': True}
    id_rt = Column(Integer, primary_key=True, index=True)
    nomor_rt = Column(Integer, nullable=False)
    id_rw = Column(Integer, ForeignKey("rw.id_rw", ondelete="CASCADE"), nullable=False, index=True)
    polygon = Column(Geometry(geometry_type="MULTIPOLYGON", srid=4326), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


class Desa(Base):
    __tablename__ = "desa"
    __table_args__ = {'extend_existing': True}
    id_desa = Column(Integer, primary_key=True, index=True)
    polygon = Column(Geometry(geometry_type="MULTIPOLYGON", srid=4326), nullable=False)
    nama_desa = Column(String(100), nullable=False)
    kecamatan = Column(String(100), nullable=True)
    kabupaten = Column(String(100), nullable=True)
    provinsi = Column(String(100), nullable=True)
    luas_ha = Column(Float, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
