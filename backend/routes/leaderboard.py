from fastapi import APIRouter, HTTPException
from config import get_db
from websocket_manager import manager

leaderboard_router = APIRouter()
db = get_db()

@leaderboard_router.get("/leaderboard")
async def get_leaderboard():
    """Get all students ranked by total stars"""
    try:
        students_ref = db.collection('students')
        students = students_ref.stream()
        leaderboard_data = []
        
        for student in students:
            student_data = student.to_dict()
            progress = student_data.get('progress', {})
            total_stars = progress.get('total_stars', 0)
            # Only include students with progress
            if total_stars > 0:
                leaderboard_data.append({
                    'uid': student.id,
                    'nickname': student_data.get('nickname', 'Unknown'),
                    'total_stars': total_stars
                })
        # Sort by total_stars in descending order
        leaderboard_data.sort(key=lambda x: x['total_stars'], reverse=True)
        # Broadcast top 5 to WebSocket clients
        top5 = leaderboard_data[:5]
        await manager.broadcast_leaderboard_update(top5)
        
        return {
            "leaderboard": leaderboard_data,
            "total_players": len(leaderboard_data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@leaderboard_router.get("/leaderboard/top5")
async def get_top5_leaderboard():
    """Get top 5 students for quick access"""
    try:
        full_leaderboard = await get_leaderboard()
        return {
            "top5": full_leaderboard["leaderboard"][:5]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))