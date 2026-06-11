from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
import os
from ...services.firebase_service import create_user, get_user_by_email

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()
JWT_SECRET = os.getenv("JWT_SECRET", "pelo-secret")
JWT_ALGORITHM = "HS256"

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    phone: str
    password: str
    securityPhone: str = ""
    nextOfKinWhatsApp: str = ""
    neighbourhoodGroupLink: str = ""
    securityCompany: str = ""
    fallDetectionEnabled: bool = True
    tier: str = "standard"  # standard = R29, needy = R19

class UserLogin(BaseModel):
    email: EmailStr
    password: str

def create_access_token(data: dict):
    expire = datetime.utcnow() + timedelta(days=7)
    data.update({"exp": expire})
    return jwt.encode(data, JWT_SECRET, algorithm=JWT_ALGORITHM)

@router.post("/register")
async def register(user: UserRegister):
    existing = await get_user_by_email(user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed = pwd_context.hash(user.password)
    user_data = user.dict()
    user_data["password"] = hashed
    user_data["trialStartDate"] = datetime.utcnow().isoformat()
    user_data["trialEndDate"] = (datetime.utcnow() + timedelta(days=7)).isoformat()
    user_data["subscriptionStatus"] = "trial"
    user_data["tierApproved"] = user.tier == "standard"  # needy needs admin approval
    
    user_id = await create_user(user_data)
    token = create_access_token({"sub": user.email, "userId": user_id})
    
    user_data.pop("password")
    return {"token": token, "user": {"userId": user_id, **user_data}}

@router.post("/login")
async def login(user: UserLogin):
    db_user = await get_user_by_email(user.email)
    if not db_user or not pwd_context.verify(user.password, db_user.get("password")):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": user.email, "userId": db_user.get("userId")})
    db_user.pop("password", None)
    return {"token": token, "user": db_user}
