from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from dependencies import supabase, hash_password, verify_password, create_token, get_current_user
import random, string, hashlib, os, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

router = APIRouter(prefix="/auth", tags=["auth"])


class ForgotPasswordRequest(BaseModel):
    email: str

class VerifyCodeRequest(BaseModel):
    email: str
    code: str

class ResetPasswordRequest(BaseModel):
    reset_token: str
    new_password: str

class RegisterRequest(BaseModel):
    first_name: str
    middle_name: str = ""
    last_name: str
    username: str
    password: str
    role: str
    birthday: Optional[str] = None
    age: Optional[int] = None
    phone_number: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    full_name: str
    user_id: int
    email: str


@router.post("/register", status_code=201)
async def register(body: RegisterRequest):
    if body.role not in ("receptionist", "veterinary"):
        raise HTTPException(400, "Invalid role.")
    existing = supabase.table("USERS").select("id").eq("Email", body.username).execute()
    if existing.data:
        raise HTTPException(409, "An account with this email already exists")

    hashed = hash_password(body.password)
    insert_data = {
        "FirstName":  body.first_name.strip(),
        "MiddleName": body.middle_name.strip(),
        "LastName":   body.last_name.strip(),
        "Role":       body.role,
        "Email":      body.username.strip(),
        "Password":   hashed,
    }
    if body.birthday:     insert_data["Birthday"]   = body.birthday
    if body.age:          insert_data["Age"]         = body.age
    if body.phone_number: insert_data["PhoneNumber"] = body.phone_number

    result = supabase.table("USERS").insert(insert_data).execute()
    if not result.data:
        raise HTTPException(500, "Could not create user.")
    return {"message": "Account created successfully"}


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest):
    result = supabase.table("USERS").select("*").eq("Email", body.username).execute()
    if not result.data:
        raise HTTPException(401, "Invalid username or password")

    user = result.data[0]
    if not verify_password(body.password, user["Password"]):
        raise HTTPException(401, "Invalid username or password")

    full_name = f"{user.get('FirstName', '')} {user.get('LastName', '')}".strip()
    token = create_token(user["id"], user["Email"], user["Role"], full_name)
    return TokenResponse(
        access_token=token,
        role=user["Role"],
        full_name=full_name,
        user_id=user["id"],
        email=user["Email"],
    )


@router.get("/me")
async def me(user=Depends(get_current_user)):
    return user



def send_reset_email(to_email: str, code: str):
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Password Reset Code — Dr. Rosario Vet Clinic"
    msg["From"]    = smtp_user
    msg["To"]      = to_email

    html = f"""
    <div style="font-family:DM Sans,sans-serif;max-width:480px;margin:auto;padding:2rem;border:1px solid #e5e7eb;border-radius:12px;">
      <div style="background:linear-gradient(135deg,#0A4F29,#1a6b3c);padding:1.25rem;border-radius:8px;margin-bottom:1.5rem;">
        <h2 style="color:white;margin:0;font-size:1.1rem;">Dr. Rosario Veterinary Clinic</h2>
        <p style="color:rgba(255,255,255,0.7);margin:4px 0 0;font-size:0.8rem;">Password Reset Request</p>
      </div>
      <p style="color:#374151;font-size:0.9rem;">Your password reset code is:</p>
      <div style="text-align:center;margin:1.5rem 0;">
        <span style="font-size:2.5rem;font-weight:700;color:#0A4F29;letter-spacing:0.5rem;background:#F0FFF0;padding:0.75rem 1.5rem;border-radius:10px;border:2px solid #A7CDBB;">
          {code}
        </span>
      </div>
      <p style="color:#6b7280;font-size:0.82rem;">This code expires in <strong>15 minutes</strong>. Do not share this code with anyone.</p>
      <p style="color:#6b7280;font-size:0.82rem;">If you did not request a password reset, please ignore this email.</p>
    </div>
    """
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, to_email, msg.as_string())



@router.post("/forgot-password")
async def forgot_password(body: ForgotPasswordRequest):
    result = supabase.table("USERS").select("id, Email").eq("Email", body.email).execute()
    if not result.data:
        return {"message": "If that email exists, a code has been sent."}

    user = result.data[0]

    code = ''.join(random.choices(string.digits, k=6))
    expires_at = (datetime.utcnow() + timedelta(minutes=15)).isoformat()

    supabase.table("USERS").update({
        "reset_code":     code,
        "reset_code_exp": expires_at,
        "reset_token":    None,
    }).eq("id", user["id"]).execute()

    try:
        send_reset_email(body.email, code)
    except Exception as e:
        raise HTTPException(500, f"Failed to send email: {str(e)}")

    return {"message": "If that email exists, a code has been sent."}


@router.post("/verify-reset-code")
async def verify_reset_code(body: VerifyCodeRequest):
    result = supabase.table("USERS").select(
        "id, reset_code, reset_code_exp"
    ).eq("Email", body.email).execute()

    if not result.data:
        raise HTTPException(400, "Invalid email or code")

    user = result.data[0]
    stored_code = user.get("reset_code")
    expires_at  = user.get("reset_code_exp")

    if not stored_code or stored_code != body.code:
        raise HTTPException(400, "Invalid code")

    if not expires_at or datetime.utcnow() > datetime.fromisoformat(expires_at):
        raise HTTPException(400, "Code has expired. Please request a new one.")

    reset_token = ''.join(random.choices(string.ascii_letters + string.digits, k=64))

    supabase.table("USERS").update({
        "reset_code":     None,
        "reset_code_exp": None,
        "reset_token":    reset_token,
    }).eq("id", user["id"]).execute()

    return {"reset_token": reset_token}


@router.post("/reset-password")
async def reset_password(body: ResetPasswordRequest):
    result = supabase.table("USERS").select("id").eq("reset_token", body.reset_token).execute()

    if not result.data:
        raise HTTPException(400, "Invalid or expired reset token")

    user = result.data[0]

    hashed = hash_password(body.new_password)

    supabase.table("USERS").update({
        "Password":    hashed,  
        "reset_token": None,
    }).eq("id", user["id"]).execute()

    return {"message": "Password reset successfully"}