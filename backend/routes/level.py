from fastapi import APIRouter, HTTPException
from config import get_db

db = get_db()
levels_router = APIRouter()

@levels_router.get("/{level_id}/tasks")
async def get_level_tasks(level_id: int):
    try:
        # Validate level_id range if needed
        if level_id < 1 or level_id > 7: 
            raise HTTPException(status_code=400, detail="Invalid level ID")
            
        doc_ref = db.collection('levels').document(str(level_id))
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Level not found")
            
        level_data = doc.to_dict()
        return {
            "level": level_id, 
            "tasks": level_data.get("tasks", [])
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Level ID must be an integer")
    except Exception as e:
        print(f"Error fetching level {level_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")