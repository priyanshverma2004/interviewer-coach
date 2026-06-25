import uuid
from datetime import datetime
import gemini_service
import utils

def initialize_session(session, job_role, job_description, resume, difficulty, num_questions):
    """
    Initialize a new interview session structure.
    Save the state in a server-side JSON file and store the session_id in the client cookie.
    """
    # Clear previous active interview
    clear_session(session)
    
    session_id = str(uuid.uuid4())
    
    # Generate questions via service
    questions = gemini_service.generate_questions(
        job_role=job_role,
        job_description=job_description,
        resume=resume,
        difficulty=difficulty,
        num_questions=num_questions
    )
    
    # Structure active session data
    active_data = {
        'session_id': session_id,
        'job_role': job_role,
        'job_description': job_description,
        'resume': resume,
        'difficulty': difficulty,
        'num_questions': len(questions),
        'questions': questions, # List of {"id": X, "question": "..."}
        'answers': {},         # Keyed by question ID string
        'evaluations': {},     # Keyed by question ID string, stores single evaluations
        'current_index': 0,
        'completed': False
    }
    
    # Save active session data to file
    utils.save_active_session(session_id, active_data)
    
    # Save only the session ID in Flask session cookie
    session['active_session_id'] = session_id
    session.modified = True
    return session_id

def get_interview_data(session):
    """Get active interview data dict from server-side file."""
    session_id = session.get('active_session_id')
    if not session_id:
        return None
    return utils.load_active_session(session_id)

def get_current_question(session):
    """Returns the current question object or None."""
    data = get_interview_data(session)
    if not data:
        return None
    idx = data.get('current_index', 0)
    questions = data.get('questions', [])
    if 0 <= idx < len(questions):
        return questions[idx]
    return None

def submit_current_answer(session, answer_text):
    """
    Saves answer for current question and runs evaluation.
    Then increments current_index and updates the active session file.
    """
    session_id = session.get('active_session_id')
    if not session_id:
        return False
        
    data = utils.load_active_session(session_id)
    if not data:
        return False
        
    idx = data.get('current_index', 0)
    questions = data.get('questions', [])
    if idx < 0 or idx >= len(questions):
        return False
        
    question_obj = questions[idx]
    q_id = str(question_obj.get('id'))
    q_text = question_obj.get('question')
    
    # Save the answer
    data['answers'][q_id] = answer_text
    
    # Run evaluation via Gemini Service
    eval_result = gemini_service.evaluate_answer(q_text, answer_text)
    data['evaluations'][q_id] = eval_result
    
    # Advance to next question
    data['current_index'] = idx + 1
    if data['current_index'] >= len(questions):
        data['completed'] = True
        
    # Save progress back to file
    utils.save_active_session(session_id, data)
    return True

def compile_and_save_report(session):
    """
    Take all active session responses, generate final performance report,
    save to files, and clear session.
    """
    session_id = session.get('active_session_id')
    if not session_id:
        return None
        
    data = utils.load_active_session(session_id)
    if not data or not data.get('completed', False):
        return None
        
    # Reconstruct QA list for final report generation
    qa_history = []
    for q in data.get('questions', []):
        q_id = str(q.get('id'))
        qa_history.append({
            'id': q.get('id'),
            'question': q.get('question'),
            'answer': data['answers'].get(q_id, ''),
            'evaluation': data['evaluations'].get(q_id, {})
        })
        
    # Generate final report
    final_report = gemini_service.generate_final_report(
        job_role=data.get('job_role'),
        difficulty=data.get('difficulty'),
        QA_history=qa_history
    )
    
    # Pack report metadata and save to JSON file database
    report_db_entry = {
        'session_id': session_id,
        'job_role': data.get('job_role'),
        'difficulty': data.get('difficulty'),
        'job_description': data.get('job_description'),
        'resume': data.get('resume'),
        'qa_history': qa_history,
        'overall_score': final_report.get('overall_score', 0),
        'overall_feedback': final_report.get('overall_feedback', ''),
        'categorical_scores': final_report.get('categorical_scores', {}),
        'top_skills': final_report.get('top_skills', []),
        'key_recommendations': final_report.get('key_recommendations', []),
        'created_at': datetime.now().isoformat()
    }
    
    # Save
    saved_session_id = utils.save_interview_report(report_db_entry)
    
    # Delete active session file and clear session
    utils.delete_active_session(session_id)
    clear_session(session)
    return saved_session_id

def clear_session(session):
    """Clears the active interview session from cookie and server storage."""
    session_id = session.pop('active_session_id', None)
    if session_id:
        utils.delete_active_session(session_id)
    session.modified = True

