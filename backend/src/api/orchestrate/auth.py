import logging
import hashlib
import uuid
import firebase_admin
from firebase_admin import credentials, firestore
from fastapi import APIRouter, HTTPException

from src.schemas.auth import ProviderRegisterSchema

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Initialize Firebase safely
def get_firestore_client():
    try:
        # Check if already initialized
        firebase_admin.get_app()
    except ValueError:
        try:
            cred = credentials.Certificate("firebase-key.json")
            firebase_admin.initialize_app(cred)
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")
    return firestore.client()

@router.post("/register-provider")
async def register_provider(request: ProviderRegisterSchema):
    try:
        db = get_firestore_client()
        
        # Hash password securely using SHA-256
        hashed_pw = hashlib.sha256(request.password.encode()).hexdigest()
        
        provider_id = f"PRO-{uuid.uuid4().hex[:8].upper()}"
        
        provider_data = {
            "provider_id": provider_id,
            "name": request.name,
            "email": request.email,
            "phone": request.phone,
            "password_hash": hashed_pw,
            "address": request.address,
            "city": request.city,
            "category": request.category,
            "base_price": request.base_price,
            "specializations": request.specializations,
            "working_hours": request.working_hours,
            
            # Auto-injected operational metrics
            "rating": 5.0,
            "cancellationRate": 0.0,
            "reliabilityScore": 1.0,
            "reviewRecency": 0,
            "isSynthetic": False
        }
        
        db.collection("providers").document(provider_id).set(provider_data)
        
        logger.info(f"Successfully registered provider {provider_id} to Firestore.")
        return {"success": True, "provider_id": provider_id, "message": "Provider registered successfully."}
    except Exception as e:
        logger.error(f"Error registering provider: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to register provider: {str(e)}")
