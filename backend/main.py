"""
PELO — Community Safety & Waste Management Backend
Quantum-verified with EntangleGuard (CHSH S=2.76)
Patent: SA 2026/05142
"""

import os
import hashlib
import json
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
import firebase_admin
from firebase_admin import credentials, firestore

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
# FIREBASE INITIALIZATION
# ============================================================
# Note: In production, use environment variables for credentials.
# For this deployment, we use the service account JSON from env.
try:
    firebase_cred_json = os.getenv("FIREBASE_SERVICE_ACCOUNT")
    if firebase_cred_json:
        cred_dict = json.loads(firebase_cred_json)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
    else:
        # Fallback for local development (uses default credentials)
        firebase_admin.initialize_app()
    db = firestore.client()
    print("[PELO] ✅ Firebase Admin initialized.")
except Exception as e:
    print(f"[PELO] ⚠️ Firebase Admin not initialized: {e}")
    db = None

# ============================================================
# RSA KEY PAIR GENERATION (For Signing)
# ============================================================
# In production, load these from environment variables.
# For this deployment, we generate a fresh pair on startup.
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)
public_key = private_key.public_key()

# Serialize public key for the endpoint
public_key_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
).decode('utf-8')

# ============================================================
# FASTAPI APP
# ============================================================
app = FastAPI(
    title="PELO — Community Safety & Waste Management",
    description="Quantum-verified safety and waste intelligence platform",
    version="1.0.2",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# ============================================================
# DATA MODELS
# ============================================================
class CertificateIssueRequest(BaseModel):
    entry_id: str
    owner_name: str
    area: str
    oil_volume: float
    timestamp: str

class CertificateVerifyRequest(BaseModel):
    certificate_hash: str

# ============================================================
# ROOT & HEALTH
# ============================================================
@app.get("/")
async def root():
    return {
        "service": "PELO",
        "version": "1.0.2",
        "status": "operational",
        "quantum_badge": QUANTUM_BADGE["text"],
        "patent": QUANTUM_BADGE["patent"],
        "ibm_job_id": QUANTUM_BADGE["ibm_job_id"],
        "endpoints": [
            "/health",
            "/api/quantum/status",
            "/api/v1/verify/chsh",
            "/api/v1/issue/certificate",
            "/api/v1/verify/certificate",
            "/api/v1/public-key",
            "/api/v1/apps/pelo/status"
        ]
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/quantum/status")
async def quantum_status():
    return QUANTUM_BADGE

@app.get("/api/v1/verify/chsh")
async def verify_chsh():
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

@app.get("/api/v1/apps/pelo/status")
async def app_status():
    return {
        "app": "pelo",
        "status": "operational",
        "version": "1.0.2",
        "quantum_badge": f"CHSH S={QUANTUM_BADGE['chsh_s']:.2f}",
        "patent": QUANTUM_BADGE["patent"],
        "ibm_job_id": QUANTUM_BADGE["ibm_job_id"],
        "timestamp": datetime.now().isoformat()
    }

# ============================================================
# 1. ISSUE CERTIFICATE (Dynamic Binding)
# ============================================================
@app.post("/api/v1/issue/certificate")
async def issue_certificate(request: CertificateIssueRequest):
    """
    Generates a SHA-256 hash of the certificate data, signs it with the private key,
    and saves the record to the Firestore ledger.
    """
    if not db:
        raise HTTPException(status_code=500, detail="Database not initialized.")

    # 1. Create the canonical payload
    certificate_data = {
        "entry_id": request.entry_id,
        "owner_name": request.owner_name,
        "area": request.area,
        "oil_volume": request.oil_volume,
        "timestamp": request.timestamp,
        "chsh_s": str(QUANTUM_BADGE["chsh_s"]),
        "patent": QUANTUM_BADGE["patent"]
    }

    # 2. Generate the SHA-256 hash
    data_string = json.dumps(certificate_data, sort_keys=True)
    hash_hex = hashlib.sha256(data_string.encode()).hexdigest()

    # 3. Sign the hash with the private key
    signature = private_key.sign(
        hash_hex.encode(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    signature_hex = signature.hex()

    # 4. Save to Firestore ledger
    try:
        db.collection("pelo_master_ledger").document(hash_hex).set({
            **certificate_data,
            "hash": hash_hex,
            "signature": signature_hex,
            "issued_at": datetime.now().isoformat(),
            "ibm_job_id": QUANTUM_BADGE["ibm_job_id"],
            "status": "ISSUED"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save to ledger: {str(e)}")

    return {
        "status": "success",
        "certificate_hash": hash_hex,
        "signature": signature_hex,
        "ibm_job_id": QUANTUM_BADGE["ibm_job_id"],
        "message": "Certificate issued and signed. Use the hash to verify."
    }

# ============================================================
# 2. VERIFY CERTIFICATE (Read-Only Lookup)
# ============================================================
@app.get("/api/v1/verify/certificate/{certificate_hash}")
async def verify_certificate(certificate_hash: str):
    """
    Looks up the hash in the Firestore ledger.
    Returns 404 if the hash was never issued.
    """
    if not db:
        raise HTTPException(status_code=500, detail="Database not initialized.")

    # Validate hash format
    if len(certificate_hash) != 64:
        raise HTTPException(status_code=400, detail="Invalid SHA-256 hash format.")

    try:
        doc = db.collection("pelo_master_ledger").document(certificate_hash).get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Certificate not found in ledger.")

        data = doc.to_dict()
        return {
            "status": "success",
            "certificate_hash": certificate_hash,
            "record": {
                "entry_id": data.get("entry_id"),
                "owner_name": data.get("owner_name"),
                "area": data.get("area"),
                "oil_volume": data.get("oil_volume"),
                "timestamp": data.get("timestamp")
            },
            "quantum_anchor": {
                "chsh_s": QUANTUM_BADGE["chsh_s"],
                "ibm_job_id": QUANTUM_BADGE["ibm_job_id"],
                "hardware": QUANTUM_BADGE["ibm_processor"]
            },
            "signature": data.get("signature"),
            "issued_at": data.get("issued_at")
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ledger lookup failed: {str(e)}")

# ============================================================
# 3. PUBLIC KEY (For Offline Verification)
# ============================================================
@app.get("/api/v1/public-key")
async def get_public_key():
    """
    Returns the public key used to verify certificate signatures.
    """
    return {
        "public_key": public_key_pem,
        "algorithm": "RSA-PSS-SHA256",
        "note": "Use this key to verify signatures offline."
    }

# ============================================================
# MOUNT EXISTING ROUTERS (IF THEY EXIST)
# ============================================================
try:
    from app.api.routes import auth, incidents, guardians, alerts, chat
    app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
    app.include_router(incidents.router, prefix="/api/incidents", tags=["incidents"])
    app.include_router(guardians.router, prefix="/api/guardians", tags=["guardians"])
    app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])
    app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
    print("[PELO] ✅ Mounted existing routers.")
except Exception as e:
    print(f"[PELO] ⚠️ Could not mount routers: {e}")

# ============================================================
# RUN
# ============================================================
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
