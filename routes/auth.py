from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta
from database import get_db
from models import Admin
import os

router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def get_password_hash(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_admin(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    admin = db.query(Admin).filter(Admin.username == username).first()
    if admin is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return admin


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    admin = db.query(Admin).filter(Admin.username == form_data.username).first()
    if not admin or not verify_password(form_data.password, admin.password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    admin.last_login = datetime.utcnow()
    db.commit()

    access_token = create_access_token(data={"sub": admin.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register")
def register(username: str, password: str, db: Session = Depends(get_db)):
    existing = db.query(Admin).filter(Admin.username == username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = get_password_hash(password)
    admin = Admin(username=username, password=hashed_password)
    db.add(admin)
    db.commit()
    return {"message": "Admin created successfully"}
