import json
import os
import sys

class HistoryManager:
    def __init__(self, filename="history.json"):
        # Get project root (where run.py/Data/ are)
        if getattr(sys, 'frozen', False):
            # When bundled, use Application Support to avoid read-only errors
            app_root = os.path.expanduser("~/Library/Application Support/ScreenTutor")
        else:
            # During development, use the project root
            # Assuming HistoryManager is in app/backend/memory/
            app_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        
        self.filepath = os.path.join(app_root, "Data", filename)
        self._ensure_data_dir()
        self.history = self._load()

    def _ensure_data_dir(self):
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)

    def _load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_question(self, question, mode):
        # Avoid duplicates
        if any(h['question'] == question for h in self.history):
            return
            
        self.history.append({
            "question": question,
            "mode": mode,
            "timestamp": os.path.getmtime(self.filepath) if os.path.exists(self.filepath) else 0 
        })
        self._persist()

    def _persist(self):
        with open(self.filepath, 'w') as f:
            json.dump(self.history, f, indent=4)

    def get_all_questions(self):
        return [h['question'] for h in self.history]
