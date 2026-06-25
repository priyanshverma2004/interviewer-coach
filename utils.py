import os
import json
import uuid
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

def ensure_data_dir():
    """Ensure the data directory exists."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def save_interview_report(report_data):
    """Save an interview report as a JSON file."""
    ensure_data_dir()
    session_id = report_data.get('session_id') or str(uuid.uuid4())
    report_data['session_id'] = session_id
    if 'created_at' not in report_data:
        report_data['created_at'] = datetime.now().isoformat()
    
    filename = f"report_{session_id}.json"
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=4, ensure_ascii=False)
    return session_id

def load_interview_report(session_id):
    """Load an interview report by its session ID."""
    ensure_data_dir()
    filename = f"report_{session_id}.json"
    filepath = os.path.join(DATA_DIR, filename)
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None
    return None

def load_all_reports():
    """Load all saved interview reports."""
    ensure_data_dir()
    reports = []
    for filename in os.listdir(DATA_DIR):
        if filename.startswith('report_') and filename.endswith('.json'):
            filepath = os.path.join(DATA_DIR, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    reports.append(json.load(f))
            except Exception:
                continue
    # Sort by created_at descending (newest first)
    reports.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    return reports

def format_datetime(iso_string):
    """Format an ISO 8601 string to a readable format."""
    try:
        dt = datetime.fromisoformat(iso_string)
        return dt.strftime("%B %d, %Y - %I:%M %p")
    except Exception:
        return iso_string

def save_active_session(session_id, data):
    """Save active interview session data to a JSON file."""
    ensure_data_dir()
    filepath = os.path.join(DATA_DIR, f"active_{session_id}.json")
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_active_session(session_id):
    """Load active interview session data from a JSON file."""
    ensure_data_dir()
    filepath = os.path.join(DATA_DIR, f"active_{session_id}.json")
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None
    return None

def delete_active_session(session_id):
    """Delete active interview session file."""
    ensure_data_dir()
    filepath = os.path.join(DATA_DIR, f"active_{session_id}.json")
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
        except Exception:
            pass

