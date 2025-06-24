from config import get_db

db = get_db()

# Define level-to-task mappings with translations
levels_data = {
    "1": {
        "tasks": ["DOG", "CAT", "BUS"],
        "translations": ["බල්ලා", "පූසා", "බස් එක"]
    },
    "2": {
        "tasks": ["PLANE", "BIRD", "FROG"],
        "translations": ["ගුවන් යානය", "කුරුල්ලා", "ගෙම්බා"]
    },
    "3": {
        "tasks": ["WATER", "CLOUD", "SNAKE"],
        "translations": ["වතුර", "වලාකුළ", "සර්පයා"]
    },
    "4": {
        "tasks": ["MARKET", "BUTTON", "CAMERA"],
        "translations": ["වෙළඳපොළ", "බොත්තම", "කැමරාව"]
    },
    "5": {
        "tasks": ["LANTERN", "DRAGON", "BOTTLE"],
        "translations": ["පහන", "මකරා", "බෝතලය"]
    },
    "6": {
        "tasks": ["MONSTER", "HUNTER", "TREES"],
        "translations": ["රකුසා", "දඩයක්කාරයා", "ගස්"]
    }
}

# Update Firestore with translations (using merge=True to preserve existing data)
for level_id, data in levels_data.items():
    db.collection('levels').document(level_id).set({
        "translations": data["translations"]
    }, merge=True)

print("✅ Translations successfully added to existing levels in Firestore.")