from pydantic import BaseModel
from typing import Dict, List, Optional

class StudentSignup(BaseModel):
    email: str
    password: str
    nickname: str

class LevelProgress(BaseModel):
    level_id: int
    stars_earned: int
    tasks_completed: List[int]  # [1, 2, 3] for completed tasks
    is_unlocked: bool
    completed_at: Optional[str] = None 

class TaskResponse(BaseModel):
    level: int
    tasks: List[str]

class PredictTaskRequest(BaseModel):
    images: List[str]  # base64 encoded images, one per character

class StudentProgress(BaseModel):
    current_level: int
    total_stars: int
    levels: Dict[int, LevelProgress]

class AdminSignup(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str