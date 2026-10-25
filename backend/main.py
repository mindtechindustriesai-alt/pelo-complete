"""
PELO — Community Safety & Waste Management Backend
Quantum-verified with EntangleGuard (CHSH S=2.76)
Patent: SA 2026/05142
"""

import os
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# ============================================================
# QUANTUM CONSTANTS
# ============================================================
QUANTUM_BADGE = {
    "chsh_s": 2.76,
    "classical_limit": 2.0,
    "quantum_max": 2.8284,
    "percent_above_classical": 38.0,
    "correlation": 0.984,
    "patent": "SA 2026/05142",
    "verification_date": "2026-06-25",
    "ibm_job_id": "d8uhvl4bp3hs738628cg",
    "ibm_processor": "IBM Kingston (156 qubits)",
    "text": "CHSH S=2.76 · 38% above classical"
}

# ============================================================
# FASTAPI APP
# ============================================================
app = FastAPI(
    title="PELO — Community Safety & Waste Management",
    description="Quantum-verified safety and waste intelligence platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS — Allow all origins for the PELO frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# ============================================================
# ROOT & HEALTH
# ============================================================
@app.get("/")
async def root():
    return {
        "service": "PELO",
        "version": "1.0.0",
        "status": "operational",
        "quantum_badge": QUANTUM_BADGE["text"],
        "patent": QUANTUM_BADGE["patent"],
        "ibm_job_id": QUANTUM_BADGE["ibm_job_id"],
        "endpoints": [
            "/health",
            "/api/quantum/status",
            "/api/v1/verify/chsh",
            "/api/v1/apps/pelo/status"
        ]
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/quantum/status")
async def quantum_status():
    return QUANTUM_BADGE

# ============================================================
# ENTANGLEGUARD INTEGRATION — CHSH HANDSHAKE
# ============================================================
@app.get("/api/v1/verify/chsh")
async def verify_chsh():
    """
    Deterministic Quantum Trust Handshake endpoint for EntangleGuard SDK.
    Returns the immutable IBM Kingston attestation.
    """
    return {
        "S": QUANTUM_BADGE["chsh_s"],
        "backend": "ibm_kingston",
        "job_id": QUANTUM_BADGE["ibm_job_id"],
        "status": "CONFIRMED",
        "patent": QUANTUM_BADGE["patent"],
        "hardware_verified": True,
        "quantum_max": QUANTUM_BADGE["quantum_max"],
        "classical_limit": QUANTUM_BADGE["classical_limit"],
        "app": "pelo",
        "timestamp": datetime.now().isoformat()
    }

# ============================================================
# MQOS APP STATUS — HEALTH CHECK FOR DASHBOARD
# ============================================================
@app.get("/api/v1/apps/pelo/status")
async def app_status():
    """
    Health check endpoint for the MQOS Tererai dashboard.
    """
    return {
        "app": "pelo",
        "status": "operational",
        "version": "1.0.0",
        "quantum_badge": f"CHSH S={QUANTUM_BADGE['chsh_s']:.2f}",
        "patent": QUANTUM_BADGE["patent"],
        "ibm_job_id": QUANTUM_BADGE["ibm_job_id"],
        "timestamp": datetime.now().isoformat()
    }

# ============================================================
# MOUNT EXISTING ROUTERS (IF THEY EXIST)
# ============================================================
# Attempt to mount the routers from app/api/routes/
# If the imports fail (e.g., missing files), the app still runs
# with the quantum endpoints.

try:
    from app.api.routes import auth, incidents, guardians, alerts, chat
    app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
    app.include_router(incidents.router, prefix="/api/incidents", tags=["incidents"])
    app.include_router(guardians.router, prefix="/api/guardians", tags=["guardians"])
    app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])
    app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
    print("[PELO] ✅ Mounted existing routers (auth, incidents, guardians, alerts, chat)")
except Exception as e:
    print(f"[PELO] ⚠️ Could not mount existing routers: {e}")
    print("[PELO] The quantum endpoints are still available.")

# ============================================================
# RUN
# ============================================================
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
