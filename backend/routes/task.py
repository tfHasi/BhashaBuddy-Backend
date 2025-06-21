from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import List
from PIL import Image
import io
from datetime import datetime
from config import get_db
from scripts.inference import predict_word_from_images

predict_router = APIRouter()
db = get_db()

@predict_router.post("/student/{student_uid}/predict-task")
async def predict_task(
    student_uid: str,
    level_id: int = Form(...),
    task_id: int = Form(...),
    images: List[UploadFile] = File(...)
):
    try:
        if not (3 <= len(images) <= 6):
            raise HTTPException(status_code=400, detail="Provide 3 to 6 images")

        # Fetch level and task
        level_doc = db.collection("levels").document(str(level_id)).get()
        if not level_doc.exists:
            raise HTTPException(status_code=404, detail="Level not found")

        tasks = level_doc.to_dict().get("tasks", [])
        if task_id >= len(tasks):
            raise HTTPException(status_code=400, detail="Invalid task ID")

        target_word = tasks[task_id]
        if len(images) != len(target_word):
            raise HTTPException(
                status_code=400,
                detail=f"Expected {len(target_word)} images for word '{target_word}'"
            )

        # Convert to PIL images
        pil_images = []
        for i, file in enumerate(images):
            if not file.content_type.startswith("image/"):
                raise HTTPException(status_code=400, detail=f"File {i+1} is not an image")
            try:
                content = await file.read()
                image = Image.open(io.BytesIO(content))
                pil_images.append(image)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Error reading image {i+1}: {str(e)}")

        # Predict word
        predicted_word = predict_word_from_images(pil_images)
        correct = predicted_word.upper() == target_word.upper()

        # Default flags
        updated = False
        stars_earned = None
        level_completed = False
        next_level_unlocked = False

        if correct:
            student_ref = db.collection('students').document(student_uid)
            student_doc = student_ref.get()

            if not student_doc.exists:
                raise HTTPException(status_code=404, detail="Student not found")

            student_data = student_doc.to_dict()
            progress = student_data.get('progress', {})
            levels = progress.get('levels', {})
            level_key = str(level_id)

            if level_key not in levels:
                raise HTTPException(status_code=400, detail="Level not unlocked")

            level_progress = levels[level_key]

            # Only update if task is not already completed
            if task_id not in level_progress['tasks_completed']:
                level_progress['tasks_completed'].append(task_id)
                level_progress['stars_earned'] = len(level_progress['tasks_completed'])
                stars_earned = level_progress['stars_earned']
                updated = True

                # Check for level completion and unlock next
                if stars_earned >= 2:
                    level_progress['completed_at'] = datetime.utcnow().isoformat()
                    level_completed = True
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
                        next_level_unlocked = True

                # Update total stars
                progress['total_stars'] = sum(lvl.get('stars_earned', 0) for lvl in levels.values())

                # Save back
                student_ref.update({'progress': progress})

        # Final response
        return {
            "student_uid": student_uid,
            "level_id": level_id,
            "task_id": task_id,
            "target_word": target_word,
            "predicted_word": predicted_word,
            "correct": correct,
            "updated": updated,
            "stars_earned": stars_earned,
            "level_completed": level_completed,
            "next_level_unlocked": next_level_unlocked
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))