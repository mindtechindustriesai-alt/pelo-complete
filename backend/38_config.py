# ============================================================
# PELO BACKEND - CONFIGURATION MANAGEMENT
# Loads environment variables with validation
# ============================================================

import os
from typing import List, Optional
from dotenv import load_dotenv

# Load .env file if present (local development)
load_dotenv()


class Config:
    """Central configuration class for PELO backend."""
    
    # ============================================================
    # APP SETTINGS
    # ============================================================
    APP_NAME: str = "PELO Backend"
    APP_VERSION: str = "2.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # ============================================================
    # API SETTINGS
    # ============================================================
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    
    # CORS
    CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "http://localhost:5500,https://pelo.netlify.app").split(",")
    
    # ============================================================
    # DEEPSEEK AI
    # ============================================================
    DEEPSEEK_API_KEY: Optional[str] = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_URL: str = "https://api.deepseek.com/v1/chat/completions"
    DEEPSEEK_MODEL: str = "deepseek-chat"
    
    # ============================================================
    # AUTH (JWT)
    # ============================================================
    JWT_SECRET: str = os.getenv("JWT_SECRET", "change-this-secret-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_DAYS: int = int(os.getenv("JWT_EXPIRY_DAYS", "30"))
    
    # ============================================================
    # FIREBASE
    # ============================================================
    FIREBASE_PROJECT_ID: Optional[str] = os.getenv("FIREBASE_PROJECT_ID")
    FIREBASE_PRIVATE_KEY: Optional[str] = os.getenv("FIREBASE_PRIVATE_KEY")
    FIREBASE_CLIENT_EMAIL: Optional[str] = os.getenv("FIREBASE_CLIENT_EMAIL")
    
    @property
    def firebase_credentials_valid(self) -> bool:
        """Check if Firebase credentials are present."""
        return all([self.FIREBASE_PROJECT_ID, self.FIREBASE_PRIVATE_KEY, self.FIREBASE_CLIENT_EMAIL])
    
    # ============================================================
    # TWILIO (WhatsApp/SMS)
    # ============================================================
    TWILIO_ACCOUNT_SID: Optional[str] = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN: Optional[str] = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_WHATSAPP_NUMBER: str = os.getenv("TWILIO_WHATSAPP_NUMBER", "+14155238886")
    TWILIO_PHONE_NUMBER: Optional[str] = os.getenv("TWILIO_PHONE_NUMBER")
    
    @property
    def twilio_configured(self) -> bool:
        """Check if Twilio is configured."""
        return bool(self.TWILIO_ACCOUNT_SID and self.TWILIO_AUTH_TOKEN)
    
    # ============================================================
    # STRIPE (Payments)
    # ============================================================
    STRIPE_SECRET_KEY: Optional[str] = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_WEBHOOK_SECRET: Optional[str] = os.getenv("STRIPE_WEBHOOK_SECRET")
    
    @property
    def stripe_configured(self) -> bool:
        """Check if Stripe is configured."""
        return bool(self.STRIPE_SECRET_KEY)
    
    # ============================================================
    # EMERGENCY NUMBERS (South Africa)
    # ============================================================
    GBV_HELPLINE: str = os.getenv("GBV_HELPLINE", "0800150150")
    GBV_SILENT_CALLBACK: str = os.getenv("GBV_SILENT_CALLBACK", "0800428428")
    CHILDLINE_NUMBER: str = os.getenv("CHILDLINE_NUMBER", "0800055555")
    SAPS_EMERGENCY: str = os.getenv("SAPS_EMERGENCY", "10111")
    AMBULANCE_EMERGENCY: str = os.getenv("AMBULANCE_EMERGENCY", "10177")
    CELL_EMERGENCY: str = os.getenv("CELL_EMERGENCY", "112")
    
    # ============================================================
    # REDIS (Rate Limiting / Caching)
    # ============================================================
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")
    
    @property
    def redis_configured(self) -> bool:
        """Check if Redis is configured."""
        return bool(self.REDIS_URL)
    
    # ============================================================
    # QUANTUM BADGE (CHSH S=2.76)
    # ============================================================
    QUANTUM_VERIFIED: bool = True
    CHSH_SCORE: float = 2.76
    CLASSICAL_LIMIT: float = 2.0
    QUANTUM_MAXIMUM: float = 2.828
    PATENT_NUMBER: str = "SA 2026/05142"
    VERIFICATION_DATE: str = "2026-03-24"
    VERIFICATION_PLATFORM: str = "Torino Quantum Processor"
    
    @property
    def percent_above_classical(self) -> float:
        """Calculate percentage above classical bound."""
        return ((self.CHSH_SCORE - self.CLASSICAL_LIMIT) / self.CLASSICAL_LIMIT) * 100
    
    @property
    def quantum_badge_text(self) -> str:
        """Return quantum badge as plain text."""
        return f"CHSH S={self.CHSH_SCORE:.2f} · {self.percent_above_classical:.0f}% above classical bound"
    
    @property
    def quantum_badge_html(self) -> str:
        """Return quantum badge as HTML."""
        return f'<span class="quantum-badge">⚛️ {self.quantum_badge_text}</span>'
    
    # ============================================================
    # VALIDATION
    # ============================================================
    def validate(self) -> List[str]:
        """Validate required configuration."""
        errors = []
        
        # Check critical keys (only if not in development mode)
        if not self.DEBUG:
            if not self.DEEPSEEK_API_KEY:
                errors.append("DEEPSEEK_API_KEY is required in production")
            if self.JWT_SECRET == "change-this-secret-in-production":
                errors.append("JWT_SECRET must be changed from default in production")
        
        return errors
    
    def __repr__(self) -> str:
        return f"<Config APP_NAME={self.APP_NAME} ENV={self.ENVIRONMENT}>"


# Singleton instance
config = Config()

# Print validation warnings on import (optional)
if config.validate():
    print(f"⚠️ Configuration warnings: {config.validate()}")
