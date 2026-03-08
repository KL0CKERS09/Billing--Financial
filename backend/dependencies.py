from supabase import create_client, Client
from jose import jwt, JWTError
from fastapi import HTTPException, Header
from datetime import datetime, timedelta
from typing import Optional
import hashlib, hmac, os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL     = os.getenv("PUBLIC_SUPABASE_URL", "https://mqcctblfleobelgageby.supabase.co")
SUPABASE_KEY     = os.getenv("PUBLIC_SUPABASE_PUBLISHABLE_DEFAULT_KEY", "sb_publishable_CAL82Zb__gMQLegRH9J7xw_EUvcv1RT")
JWT_SECRET       = os.getenv("JWT_SECRET", "KL0CKERSFREDOBENDAL123123123")
JWT_ALGO         = "HS256"
JWT_EXPIRY_HOURS = 8

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def hash_password(plain: str) -> str:
    return hashlib.sha256(f"drrosario_salt_{plain}".encode()).hexdigest()

def verify_password(plain: str, hashed: str) -> bool:
    return hmac.compare_digest(hash_password(plain), hashed)

def create_token(user_id: int, email: str, role: str, full_name: str) -> str:
    payload = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "full_name": full_name,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRY_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)

def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing or invalid Authorization header")
    token = authorization.split(" ", 1)[1]
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
    except JWTError:
        raise HTTPException(401, "Invalid or expired token")