from fastapi import APIRouter, HTTPException
from firebase_admin import auth
from config import get_db
from models.schemas import AdminSignup
import uuid

admin_router = APIRouter()
db = get_db()

@admin_router.post("/signup")
async def admin_signup(data: AdminSignup):
    try:
        user = auth.create_user(email=data.email, password=data.password)
        aid = str(uuid.uuid4())[:8].upper()
        db.collection('admins').document(user.uid).set({
            'aid': aid,
            'email': data.email,
            'type': 'admin'
        })
        return {"message": "Admin created successfully", "aid": aid}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))