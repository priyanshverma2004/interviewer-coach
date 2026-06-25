import utils

def get_dashboard_stats():
    """
    Calculate and return statistics for the user dashboard based on saved reports.
    """
    reports = utils.load_all_reports()
    
    total_interviews = len(reports)
    if total_interviews == 0:
        return {
            'total_interviews': 0,
            'average_score': 0,
            'category_averages': {
                'communication': 0,
                'technical_accuracy': 0,
                'problem_solving': 0
            },
            'top_skills': [],
            'recent_interviews': [],
            'score_trends': []
        }
    
    # Calculate average overall score
    total_score = sum(r.get('overall_score', 0) for r in reports)
    average_score = round(total_score / total_interviews)
    
    # Calculate category averages
    categories = ['communication', 'technical_accuracy', 'problem_solving']
    cat_sums = {cat: 0 for cat in categories}
    cat_counts = {cat: 0 for cat in categories}
    
    for r in reports:
        cat_scores = r.get('categorical_scores', {})
        for cat in categories:
            if cat in cat_scores:
                cat_sums[cat] += cat_scores[cat]
                cat_counts[cat] += 1
                
    cat_averages = {}
    for cat in categories:
        count = cat_counts[cat]
        cat_averages[cat] = round(cat_sums[cat] / count) if count > 0 else 0
        
    # Extract top skills
    skill_counts = {}
    for r in reports:
        for skill in r.get('top_skills', []):
            skill_counts[skill] = skill_counts.get(skill, 0) + 1
            
    # Sort skills by frequency
    sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)
    top_skills = [skill for skill, count in sorted_skills[:5]]
    
    # Prepare recent interviews list
    recent_interviews = []
    for r in reports[:10]: # Limit to 10 latest
        recent_interviews.append({
            'session_id': r.get('session_id'),
            'job_role': r.get('job_role'),
            'difficulty': r.get('difficulty'),
            'overall_score': r.get('overall_score'),
            'created_at': utils.format_datetime(r.get('created_at', ''))
        })
        
    # Prepare score trends for Chart.js (needs to be chronologically ordered)
    score_trends = []
    for r in reversed(reports[-10:]): # Max 10 items, oldest first
        date_str = ""
        created_at = r.get('created_at', '')
        try:
            # e.g., "June 24"
            dt = utils.datetime.fromisoformat(created_at)
            date_str = dt.strftime("%b %d")
        except Exception:
            date_str = created_at[:10]
            
        score_trends.append({
            'date': date_str,
            'score': r.get('overall_score', 0),
            'job_role': r.get('job_role', 'Interview')
        })
        
    return {
        'total_interviews': total_interviews,
        'average_score': average_score,
        'category_averages': cat_averages,
        'top_skills': top_skills,
        'recent_interviews': recent_interviews,
        'score_trends': score_trends
    }
