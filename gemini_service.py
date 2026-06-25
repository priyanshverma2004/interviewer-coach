import os
import json
import logging
import google.generativeai as genai
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load env variables
load_dotenv()

API_KEY = os.environ.get("GEMINI_API_KEY")
IS_MOCK_MODE = not API_KEY or API_KEY == "your_gemini_api_key_here"

if not IS_MOCK_MODE:
    genai.configure(api_key=API_KEY)
    logger.info("Gemini API configured successfully.")
else:
    logger.warning("No valid GEMINI_API_KEY found. Running in MOCK MODE for demo purposes.")

def get_gemini_model():
    """Helper to get a GenerativeModel instance."""
    if IS_MOCK_MODE:
        return None
    try:
        # Use gemini-2.5-flash as the default model
        return genai.GenerativeModel("gemini-2.5-flash")
    except Exception as e:
        logger.error(f"Error initializing Gemini Model: {e}")
        return None

def generate_questions(job_role, job_description, resume, difficulty, num_questions):
    """
    Generate tailored interview questions.
    Returns: List of dicts, e.g. [{"id": 1, "question": "..."}]
    """
    if IS_MOCK_MODE:
        return _generate_mock_questions(job_role, difficulty, num_questions)
        
    model = get_gemini_model()
    if not model:
        return _generate_mock_questions(job_role, difficulty, num_questions)

    prompt = f"""
    You are an expert technical and behavioral recruiter. Generate exactly {num_questions} interview questions tailored to the following candidate profile:
    
    Job Role: {job_role}
    Difficulty: {difficulty}
    Job Description context: {job_description or 'General industry requirements'}
    Candidate Resume context: {resume or 'Standard background'}
    
    Ensure questions are highly realistic, combining technical expertise and behavioral scenarios (STAR method format where appropriate).
    Generate the response as a JSON array of objects, where each object has:
      - 'id' (integer, starting from 1)
      - 'question' (string, the interview question)
    
    Provide ONLY the raw JSON array. Do not include markdown code block syntax (like ```json).
    """

    try:
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        questions = json.loads(response.text.strip())
        # Ensure it's a list
        if isinstance(questions, list) and len(questions) > 0:
            return questions
        else:
            raise ValueError("Response is not a non-empty JSON list")
    except Exception as e:
        logger.error(f"Gemini API generate_questions failed: {e}. Falling back to mock data.")
        return _generate_mock_questions(job_role, difficulty, num_questions)

def evaluate_answer(question, answer):
    """
    Evaluate a candidate's response to a single question.
    Returns: Dict containing score, strengths, weaknesses, suggestions, and model answer.
    """
    if IS_MOCK_MODE or not answer or len(answer.strip()) < 5:
        return _generate_mock_evaluation(question, answer)

    model = get_gemini_model()
    if not model:
        return _generate_mock_evaluation(question, answer)

    prompt = f"""
    You are an expert interviewer evaluating a candidate's answer to an interview question.
    
    Question: {question}
    Candidate's Answer: {answer}
    
    Perform a constructive evaluation. Score the answer from 0 to 10 (where 10 is flawless and 0 is blank or completely irrelevant).
    Generate the response in JSON format containing the following keys:
      - 'score': A number (integer or float) from 0 to 10.
      - 'correctness_analysis': A string explaining the correctness, technical accuracy, and depth of their answer.
      - 'strengths': A JSON array of strings outlining specific points they did well (e.g. structure, style).
      - 'weaknesses': A JSON array of strings outlining specific things they missed or did poorly.
      - 'negatives': A JSON array of strings detailing explicit incorrect statements, logical flaws, or counter-productive behaviors in their answer.
      - 'suggestions': A JSON array of strings providing concrete guidance on how to improve this answer.
      - 'model_answer': A string showing a high-quality, comprehensive sample response to this question.

    Provide ONLY the raw JSON object. Do not include markdown code block syntax (like ```json).
    """

    try:
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text.strip())
    except Exception as e:
        logger.error(f"Gemini API evaluate_answer failed: {e}. Falling back to mock evaluation.")
        return _generate_mock_evaluation(question, answer)

def generate_final_report(job_role, difficulty, QA_history):
    """
    Analyze the full interview transcript and generate a comprehensive performance report.
    QA_history: list of dicts, each having 'question', 'answer', 'evaluation' (with score, strengths, suggestions).
    """
    if IS_MOCK_MODE or not QA_history:
        return _generate_mock_final_report(job_role, difficulty, QA_history)

    model = get_gemini_model()
    if not model:
        return _generate_mock_final_report(job_role, difficulty, QA_history)

    history_summary = []
    for qa in QA_history:
        history_summary.append({
            "question": qa.get("question"),
            "answer": qa.get("answer"),
            "score": qa.get("evaluation", {}).get("score", 0),
            "strengths": qa.get("evaluation", {}).get("strengths", []),
            "suggestions": qa.get("evaluation", {}).get("suggestions", [])
        })

    prompt = f"""
    You are an expert career development coach. Based on this complete interview transcript for the role of '{job_role}' ({difficulty} level):
    
    Transcript Summary:
    {json.dumps(history_summary, indent=2)}
    
    Synthesize their performance and create a structured performance report.
    Generate the response in JSON format containing the following keys:
      - 'overall_score': An integer from 0 to 100 (representing the aggregate performance).
      - 'overall_feedback': A string summarizing their performance, strengths, and general advice.
      - 'categorical_scores': A JSON object with scores (0 to 100) for:
        - 'communication': Clarity, structure, articulation, confidence.
        - 'technical_accuracy': Correctness, detail, depth.
        - 'problem_solving': Logic, structured approach, critical thinking.
      - 'top_skills': A JSON array of strings showing the candidate's strongest areas demonstrated during the interview.
      - 'key_recommendations': A JSON array of strings containing actionable recommendations/steps they should take next to prepare.

    Provide ONLY the raw JSON object. Do not include markdown code block syntax (like ```json).
    """

    try:
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text.strip())
    except Exception as e:
        logger.error(f"Gemini API generate_final_report failed: {e}. Falling back to mock final report.")
        return _generate_mock_final_report(job_role, difficulty, QA_history)


# --- MOCK FALLBACKS FOR DEMO & TESTING ---

def _generate_mock_questions(job_role, difficulty, num_questions):
    """Fallback generator for mock questions based on job role."""
    logger.info(f"Generating mock questions for {job_role} ({difficulty})")
    
    role_lower = job_role.lower()
    
    # Pre-canned high-quality questions for standard roles
    if "software" in role_lower or "developer" in role_lower or "engineer" in role_lower or "programmer" in role_lower:
        database = [
            "Can you explain the difference between a process and a thread, and when you would use each?",
            "How do you approach designing a scalable web service that handles high traffic spikes?",
            "Tell me about a time you encountered a difficult bug. What was it, how did you find it, and what did you learn?",
            "Describe the differences between SQL and NoSQL databases. How do you decide which one to use?",
            "Explain the concept of REST APIs and what make an API 'RESTful'.",
            "What is your approach to writing clean, maintainable, and well-tested code?",
            "How would you optimize a database query that is running slowly in production?"
        ]
    elif "product" in role_lower or "pm" in role_lower:
        database = [
            "How do you prioritize features when building a product roadmap with limited resources?",
            "Tell me about a favorite product of yours. How would you improve it, and why?",
            "How do you handle disagreement with engineering teams or stakeholders about product direction?",
            "Describe a time when a product launch failed or didn't meet expectations. What did you learn?",
            "How would you design an onboarding experience for a new visual sharing mobile app?",
            "How do you define success metrics for a brand-new feature launch?"
        ]
    elif "data" in role_lower or "analyst" in role_lower or "science" in role_lower:
        database = [
            "How do you handle missing or clean dirty data before conducting an analysis?",
            "Can you explain the difference between correlation and causation with a real-world example?",
            "Explain the central limit theorem and why it is important in data science.",
            "Tell me about a time you had to explain complex data analysis findings to non-technical stakeholders.",
            "Describe how you would design an A/B test to evaluate a new pricing model.",
            "What is your favorite machine learning algorithm, and how does it work under the hood?"
        ]
    else:
        database = [
            "Tell me about yourself and why you are interested in this position.",
            "Describe a challenging project you worked on. What were the obstacles and how did you overcome them?",
            "How do you handle conflict or disagreement within a team environment?",
            "What is your process for managing your time and prioritizing tasks when working on multiple deadlines?",
            "Tell me about a time you made a mistake at work. How did you resolve it and what did you learn?",
            "Where do you see yourself in five years, and how does this role fit into your career path?"
        ]
        
    # Pick requested number of questions
    import random
    selected = []
    # Seed with static array indexing to maintain some order but keep it simple
    pool = list(database)
    for i in range(min(num_questions, len(pool))):
        selected.append({
            "id": i + 1,
            "question": pool[i % len(pool)]
        })
    return selected

def _generate_mock_evaluation(question, answer):
    """Fallback generator for evaluation of a question."""
    if not answer or len(answer.strip()) < 5:
        return {
            "score": 0,
            "correctness_analysis": "The response was blank or too short, preventing any technical correctness or communication analysis.",
            "strengths": ["None identified."],
            "weaknesses": ["The answer was blank or too short to evaluate."],
            "negatives": ["No content provided. Failed to answer the question."],
            "suggestions": ["Please provide a complete answer with details, examples, and technical depth."],
            "model_answer": "A complete answer would explain the core concept, provide a structure like the STAR method (Situation, Task, Action, Result) for behavioral questions, or cover the design trade-offs and code implementation for technical questions."
        }

    # Generate a dynamic mock feedback based on the answer length and query word matching
    length = len(answer.strip())
    score = 6.0
    if length > 250:
        score += 2.0
    if length < 50:
        score -= 2.0
        
    # Look for professional buzzwords to boost score
    buzzwords = ["star", "structure", "technical", "scale", "optimize", "experience", "example", "result", "learn", "team"]
    matches = [w for w in buzzwords if w in answer.lower()]
    score += len(matches) * 0.2
    score = min(9.5, max(1.0, round(score, 1)))

    return {
        "score": score,
        "correctness_analysis": f"The response demonstrates a correctness score of {score}/10 based on standard industry templates. The response covered key elements but lacks sufficient details on advanced implementation parameters.",
        "strengths": [
            "Provided a quick response showing willingness to explain.",
            "Communicated using relatable terms." if length > 100 else "Initiated the answer with basic context."
        ],
        "weaknesses": [
            "Could benefit from more structural organization.",
            "Lacks specific metrics or quantified outcomes." if length < 200 else "Missing some advanced technical considerations."
        ],
        "negatives": [
            "Fails to address edge cases or fallback behavior.",
            "Contains generic phrases without specific implementation evidence."
        ],
        "suggestions": [
            "Use the STAR method (Situation, Task, Action, Result) to format your response.",
            "Include concrete examples and metrics to demonstrate impact.",
            "Speak more directly about your personal role in the outcome."
        ],
        "model_answer": f"Here is how a senior candidate might answer '{question}': Focus first on setting the context clearly, detail the precise actions you took to address the problem, and conclude with the business impact or key learnings of your solution."
    }

def _generate_mock_final_report(job_role, difficulty, QA_history):
    """Fallback generator for mock final report."""
    scores = [qa.get("evaluation", {}).get("score", 6.0) for qa in QA_history] if QA_history else [7.0]
    avg_score = sum(scores) / len(scores) if scores else 7.0
    overall_percent = int(avg_score * 10)
    
    # Calculate mock categorical scores based on average
    comm_score = min(95, max(45, int(overall_percent + 2)))
    tech_score = min(95, max(45, int(overall_percent - 3)))
    problem_score = min(95, max(45, int(overall_percent + 1)))

    return {
        "overall_score": overall_percent,
        "overall_feedback": f"Overall, you demonstrated solid preparation for a {difficulty} {job_role} interview. You communicate concepts well but could improve in structural delivery (using STAR structure) and drilling deeper into technical trade-offs. Regular practice with timers will help you refine your response speed and conciseness.",
        "categorical_scores": {
            "communication": comm_score,
            "technical_accuracy": tech_score,
            "problem_solving": problem_score
        },
        "top_skills": [
            "Conceptual Understanding",
            "Clear Articulation",
            "Professional Demeanor"
        ],
        "key_recommendations": [
            "Structure behavioral answers strictly around Situation, Task, Action, and Result (STAR).",
            "For technical questions, proactively discuss edge cases and scale considerations.",
            "Practice mock speaking sessions using the voice recording mode to minimize filler words."
        ]
    }
