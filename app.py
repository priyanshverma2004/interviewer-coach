import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from dotenv import load_dotenv

# Import our backend services
import utils
import gemini_service
import interview_engine
import report_generator

# Load environment variables
load_dotenv()

app = Flask(__name__)
# Secure secret key configuration
app.secret_key = os.environ.get("SECRET_KEY", "ai_interview_coach_secret_session_key_98765")

# Register custom jinja filter for formatting ISO dates
@app.template_filter('format_date')
def format_date_filter(s):
    return utils.format_datetime(s)

@app.route("/")
def index():
    """Landing page of the application."""
    return render_template("index.html")

@app.route("/setup", methods=["GET", "POST"])
def setup():
    """Setup page for configuring the interview parameters."""
    if request.method == "POST":
        job_role = request.form.get("job_role", "Software Engineer")
        job_description = request.form.get("job_description", "")
        resume = request.form.get("resume", "")
        difficulty = request.form.get("difficulty", "Mid-level")
        try:
            num_questions = int(request.form.get("num_questions", 5))
        except ValueError:
            num_questions = 5

        # Initialize the interview session and fetch/generate questions
        try:
            interview_engine.initialize_session(
                session=session,
                job_role=job_role,
                job_description=job_description,
                resume=resume,
                difficulty=difficulty,
                num_questions=num_questions
            )
            return redirect(url_for("interview", q_index=0))
        except Exception as e:
            # If AI fails, redirect back with error or clear session
            interview_engine.clear_session(session)
            return render_template("setup.html", error=f"Failed to generate questions: {str(e)}")

    return render_template("setup.html")

@app.route("/interview/<int:q_index>", methods=["GET", "POST"])
def interview(q_index):
    """Active interview page representing a specific question index."""
    interview_data = interview_engine.get_interview_data(session)
    if not interview_data:
        return redirect(url_for("setup"))

    current_idx = interview_data.get("current_index", 0)
    questions = interview_data.get("questions", [])
    total_q = interview_data.get("num_questions", 0)

    # Enforce chronological traversal
    if q_index != current_idx:
        return redirect(url_for("interview", q_index=current_idx))

    # Handled POST submission (answering a question)
    if request.method == "POST":
        answer_text = request.form.get("answer", "").strip()
        
        # Save response and get evaluation
        success = interview_engine.submit_current_answer(session, answer_text)
        if not success:
            return redirect(url_for("setup"))
            
        # Re-check updated interview data state
        updated_data = interview_engine.get_interview_data(session)
        if updated_data and updated_data.get("completed", False):
            # Compile results, generate overall feedback, save to disk
            session_id = interview_engine.compile_and_save_report(session)
            if session_id:
                return redirect(url_for("feedback", session_id=session_id))
            else:
                return redirect(url_for("dashboard"))
        
        return redirect(url_for("interview", q_index=current_idx + 1))

    # GET request: render the active question
    question_obj = interview_engine.get_current_question(session)
    if not question_obj:
        # Fallback if something went wrong or list ended
        return redirect(url_for("setup"))

    return render_template(
        "interview.html",
        question=question_obj.get("question"),
        q_num=q_index + 1,
        total_questions=total_q,
        job_role=interview_data.get("job_role"),
        difficulty=interview_data.get("difficulty")
    )

@app.route("/feedback/<session_id>")
def feedback(session_id):
    """Display individual evaluations for each question in a session."""
    report = utils.load_interview_report(session_id)
    if not report:
        return redirect(url_for("dashboard"))
        
    return render_template("feedback.html", report=report)

@app.route("/report/<session_id>")
def report(session_id):
    """Display final overall performance analysis and charts."""
    report_data = utils.load_interview_report(session_id)
    if not report_data:
        return redirect(url_for("dashboard"))
        
    return render_template("report.html", report=report_data)

@app.route("/dashboard")
def dashboard():
    """Aggregated portfolio dashboard displaying progression charts & past reports."""
    stats = report_generator.get_dashboard_stats()
    return render_template("dashboard.html", stats=stats)

@app.route("/api/dashboard-data")
def api_dashboard_data():
    """Data endpoint feeding Chart.js rendering on client dashboard."""
    stats = report_generator.get_dashboard_stats()
    return jsonify(stats)

@app.route("/clear-session")
def clear_session_route():
    """Helper route to reset state of active interview sessions."""
    interview_engine.clear_session(session)
    return redirect(url_for("setup"))

if __name__ == "__main__":
    app.run(debug=True, port=5000)
