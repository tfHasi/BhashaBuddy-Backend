# populate_levels.py

from config import get_db

db = get_db()

# Define level-to-task mappings
levels_data = {
    "1": ["DOG", "CAT", "BUS"],
    "2": ["PLANE", "BIRD", "FROG"],
    "3": ["WATER", "CLOUD", "SNAKE"],
    "4": ["MARKET", "BUTTON", "CAMERA"],
    "5": ["LANTERN", "DRAGON", "BOTTLES"],
    "6": ["MONSTER", "HUNTERS", "TREES"]
}

# Upload to Firestore
for level_id, tasks in levels_data.items():
    db.collection('levels').document(level_id).set({
        "level_id": int(level_id),
        "tasks": tasks
    }, merge = True)

print("✅ Levels and tasks successfully populated in Firestore.")