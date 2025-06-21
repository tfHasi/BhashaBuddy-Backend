from fastapi import APIRouter, HTTPException
from firebase_admin import auth
from config import get_db
from models.schemas import LoginRequest

auth_router = APIRouter()
db = get_db()

@auth_router.post("/login")
async def login(data: LoginRequest):
    try:
        user = auth.get_user_by_email(data.email)
        
        student_doc = db.collection('students').document(user.uid).get()
        if student_doc.exists:
            student_data = student_doc.to_dict()
            return {
                "type": "student",
                "uid": user.uid,
                "sid": student_data['sid'],
                "nickname": student_data['nickname']
            }
        
        admin_doc = db.collection('admins').document(user.uid).get()
        if admin_doc.exists:
            admin_data = admin_doc.to_dict()
            return {
                "type": "admin",
                "uid": user.uid,
                "aid": admin_data['aid']
            }
        
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))