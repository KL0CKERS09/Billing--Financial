from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, dashboard, billing, reports
import os

app = FastAPI(title="Dr. Rosario Vet Clinic API")

# ✅ Read allowed origins from environment variable
# Local dev:   ALLOWED_ORIGINS=http://localhost:5173
# Production:  ALLOWED_ORIGINS=http://localhost:5173,https://your-app.vercel.app
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173")
allowed_origins = [o.strip() for o in allowed_origins_env.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(billing.router)
app.include_router(reports.router)

@app.get("/")
def root():
    return {"status": "Dr. Rosario Vet Clinic API is running"}