from fastapi import APIRouter, HTTPException
from firebase_admin import auth
from config import get_db
from models.schemas import StudentSignup, TaskResponse
import uuid
from datetime import datetime

student_router = APIRouter()
db = get_db()

@student_router.post("/signup")
async def student_signup(data: StudentSignup):
    try:
        students = db.collection('students').where('nickname', '==', data.nickname).get()
        if students:
            raise HTTPException(status_code=400, detail="Nickname already exists")
        user = auth.create_user(email=data.email, password=data.password)
        sid = str(uuid.uuid4())[:8].upper()
        # Initialize with first level unlocked
        initial_progress = {
            'current_level': 1,
            'total_stars': 0,
            'levels': {
                '1': {
                    'level_id': 1,
                    'stars_earned': 0,
                    'tasks_completed': [],
                    'is_unlocked': True,
                    'completed_at': None
                }
            }
        }
        
        db.collection('students').document(user.uid).set({
            'sid': sid,
            'email': data.email,
            'nickname': data.nickname,
            'type': 'student',
            'progress': initial_progress
        })
        return {"message": "Student created successfully", "sid": sid}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@student_router.post("/{student_uid}/complete-task")
async def complete_task(student_uid: str, level_id: int, task_id: int):
    """Complete a task and award stars"""
    try:
        # Fetch level data to validate task_id
        level_doc = db.collection('levels').document(str(level_id)).get()
        if not level_doc.exists():
            raise HTTPException(status_code=404, detail="Level not found")
        tasks = level_doc.to_dict().get("tasks", [])
        if task_id >= len(tasks):
            raise HTTPException(status_code=400, detail="Invalid task ID")
        task_word = tasks[task_id]

        # Fetch student document
        student_ref = db.collection('students').document(student_uid)
        student_doc = student_ref.get()
        if not student_doc.exists():
            raise HTTPException(status_code=404, detail="Student not found")

        student_data = student_doc.to_dict()
        progress = student_data.get('progress', {})
        levels = progress.get('levels', {})
        level_key = str(level_id)

        if level_key not in levels:
            raise HTTPException(status_code=400, detail="Level not unlocked")

        level_progress = levels[level_key]

        # Add task if not already completed
        if task_id not in level_progress['tasks_completed']:
            level_progress['tasks_completed'].append(task_id)
            level_progress['stars_earned'] = len(level_progress['tasks_completed'])

            # Unlock next level if current one is completed
            if level_progress['stars_earned'] >= 2:
                level_progress['completed_at'] = datetime.utcnow().isoformat()
                next_level = level_id + 1
                next_key = str(next_level)
                if next_key not in levels:
                    levels[next_key] = {
                        'level_id': next_level,
                        'stars_earned': 0,
                        'tasks_completed': [],
                        'is_unlocked': True,
                        'completed_at': None
                    }
                    progress['current_level'] = next_level

        progress['total_stars'] = sum(level['stars_earned'] for level in levels.values())
        student_ref.update({'progress': progress})

        return {
            "message": "Task completed successfully",
            "task_word": task_word,
            "stars_earned": level_progress['stars_earned'],
            "level_completed": level_progress['stars_earned'] >= 2,
            "next_level_unlocked": level_progress['stars_earned'] >= 2
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@student_router.get("/{student_uid}/progress")
async def get_student_progress(student_uid: str):
    """Get student's current progress"""
    try:
        student_doc = db.collection('students').document(student_uid).get()
        
        if not student_doc.exists:
            raise HTTPException(status_code=404, detail="Student not found")
        
        student_data = student_doc.to_dict()
        return {
            "sid": student_data['sid'],
            "nickname": student_data['nickname'],
            "progress": student_data.get('progress', {})
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@student_router.get("/{student_uid}/levels")
async def get_available_levels(student_uid: str):
    """Get all unlocked levels for student"""
    try:
        student_doc = db.collection('students').document(student_uid).get()
        
        if not student_doc.exists:
            raise HTTPException(status_code=404, detail="Student not found")
        
        student_data = student_doc.to_dict()
        progress = student_data.get('progress', {})
        levels = progress.get('levels', {})
        
        # Return only unlocked levels
        unlocked_levels = {
            level_id: level_data 
            for level_id, level_data in levels.items() 
            if level_data['is_unlocked']
        }
        
        return {
            "current_level": progress.get('current_level', 1),
            "total_stars": progress.get('total_stars', 0),
            "unlocked_levels": unlocked_levels
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))