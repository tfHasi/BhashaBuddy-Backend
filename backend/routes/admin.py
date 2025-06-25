from fastapi import APIRouter, HTTPException
from firebase_admin import auth
from config import get_db
from models.schemas import AdminSignup
import uuid
from typing import List, Dict, Any

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

@admin_router.get("/levels")
async def get_all_levels():
    """Get all levels with their tasks and translations"""
    try:
        levels_ref = db.collection('levels')
        levels = levels_ref.stream()
        
        levels_data = {}
        for level in levels:
            level_data = level.to_dict()
            levels_data[level.id] = {
                "level_id": level_data.get("level_id"),
                "tasks": level_data.get("tasks", []),
                "translations": level_data.get("translations", [])
            }
        
        # Sort by level_id
        sorted_levels = dict(sorted(levels_data.items(), key=lambda x: int(x[0])))
        
        return {"levels": sorted_levels}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.put("/levels/{level_id}")
async def update_level(level_id: str, tasks: List[str], translations: List[str]):
    """Update tasks and translations for a specific level"""
    try:
        if len(tasks) != len(translations):
            raise HTTPException(status_code=400, detail="Tasks and translations must have the same length")
        
        level_ref = db.collection('levels').document(level_id)
        level_doc = level_ref.get()
        
        if not level_doc.exists:
            # Create new level if it doesn't exist
            level_ref.set({
                "level_id": int(level_id),
                "tasks": tasks,
                "translations": translations
            })
        else:
            # Update existing level
            level_ref.update({
                "tasks": tasks,
                "translations": translations
            })
        
        return {"message": f"Level {level_id} updated successfully"}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid level ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.get("/students")
async def get_all_students():
    """Get all students with their progress"""
    try:
        students_ref = db.collection('students')
        students = students_ref.stream()
        
        students_data = []
        for student in students:
            student_data = student.to_dict()
            progress = student_data.get('progress', {})
            students_data.append({
                'uid': student.id,
                'sid': student_data.get('sid', 'N/A'),
                'email': student_data.get('email', 'N/A'),
                'nickname': student_data.get('nickname', 'Unknown'),
                'current_level': progress.get('current_level', 1),
                'total_stars': progress.get('total_stars', 0),
                'levels_completed': len([l for l in progress.get('levels', {}).values() if l.get('completed_at')])
            })
        
        # Sort by total_stars in descending order
        students_data.sort(key=lambda x: x['total_stars'], reverse=True)
        
        return {
            "students": students_data,
            "total_students": len(students_data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.delete("/students/{student_uid}")
async def delete_student(student_uid: str):
    """Delete a student account"""
    try:
        # Delete from Firestore
        student_ref = db.collection('students').document(student_uid)
        student_doc = student_ref.get()
        
        if not student_doc.exists:
            raise HTTPException(status_code=404, detail="Student not found")
        
        student_ref.delete()
        
        # Delete from Firebase Auth
        try:
            auth.delete_user(student_uid)
        except Exception as auth_error:
            # Continue even if auth deletion fails
            print(f"Auth deletion warning: {auth_error}")
        
        return {"message": "Student deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.get("/stats")
async def get_admin_stats():
    """Get general statistics for admin dashboard"""
    try:
        # Get student count
        students_ref = db.collection('students')
        students = list(students_ref.stream())
        total_students = len(students)
        
        # Get level count
        levels_ref = db.collection('levels')
        levels = list(levels_ref.stream())
        total_levels = len(levels)
        
        # Calculate total stars earned by all students
        total_stars_awarded = 0
        active_students = 0
        
        for student in students:
            student_data = student.to_dict()
            progress = student_data.get('progress', {})
            student_stars = progress.get('total_stars', 0)
            total_stars_awarded += student_stars
            if student_stars > 0:
                active_students += 1
        
        return {
            "total_students": total_students,
            "active_students": active_students,
            "total_levels": total_levels,
            "total_stars_awarded": total_stars_awarded
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))