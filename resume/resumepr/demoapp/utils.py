import PyPDF2
import re

def extract_text_from_pdf(pdf_file):
    """Reads PDF data and extracts textual information."""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception:
        return ""

def compute_matching_score(resume_text, job_requirements):
    """
    Compares resume text against job requirements (comma-separated list).
    Returns a percentage match based on matched target keywords.
    """
    # Clean and split requirements into individual skill components
    required_skills = [skill.strip().lower() for skill in job_requirements.split(',') if skill.strip()]
    if not required_skills:
        return 0
    
    resume_text_clean = resume_text.lower()
    matched_skills = []

    for skill in required_skills:
        # Using word boundaries to avoid false substring positives
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, resume_text_clean):
            matched_skills.append(skill)
            
    # Percentage logic
    score = int((len(matched_skills) / len(required_skills)) * 100)
    return score, ", ".join(matched_skills)
import re

def compute_matching_score(resume_text, job_requirements):
    """
    AI లాజిక్: రెజ్యూమే మరియు జాబ్ రిక్వైర్మెంట్స్ మధ్య కామన్ స్కిల్స్‌ను 
    పోల్చి చూసి మ్యాచ్ స్కోర్ (Percentage) క్యాలిక్యులేట్ చేస్తుంది.
    """
    if not resume_text or not job_requirements:
        return 0, []

    # టెక్స్ట్‌లను క్లీన్ చేసి చిన్న అక్షరాలుగా మార్చడం (Case-insensitive matching)
    resume_words = set(re.findall(r'\b\w+\b', resume_text.lower()))
    job_words = set(re.findall(r'\b\w+\b', job_requirements.lower()))

    # సాధారణంగా ఉండే ఇంగ్లీష్ పదాలను (Stopwords) తొలగించడం
    stopwords = {'and', 'or', 'the', 'in', 'of', 'with', 'a', 'to', 'for', 'an', 'is', 'on', 'at', 'by'}
    job_skills = job_words - stopwords

    # రెండు చోట్లా కామన్‌గా ఉన్న స్కిల్స్ (Matching Skills)
    matching_skills = job_skills.intersection(resume_words)

    # మ్యాచ్ స్కోర్ లెక్కించడం
    if len(job_skills) == 0:
        return 0, []
        
    score = int((len(matching_skills) / len(job_skills)) * 100)
    return score, list(matching_skills)