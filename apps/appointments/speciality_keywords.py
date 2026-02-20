"""
SPECIALITY_KEYWORDS: Maps a doctor's speciality keyword to a list of related
medical terms and synonyms. Used for appointment validation.

This uses a broad synonym approach so that e.g. "cardiac" matches "heart disease",
"chest pain", "hypertension" etc. — not just the literal word "cardiac".
"""

SPECIALITY_KEYWORDS = {
    # Cardiology
    "cardio": [
        "heart", "cardiac", "cardiovascular", "chest pain", "hypertension",
        "arrhythmia", "palpitation", "blood pressure", "coronary", "angina",
        "stroke", "atrial fibrillation", "heart failure", "echocardiogram",
        "shortness of breath", "dyspnea",
    ],
    "cardiolog": [  # matches "cardiologist", "cardiology"
        "heart", "cardiac", "cardiovascular", "chest pain", "hypertension",
        "arrhythmia", "palpitation", "blood pressure", "coronary", "angina",
        "stroke", "heart failure",
    ],
    # Neurology
    "neuro": [
        "brain", "nerve", "seizure", "epilepsy", "headache", "migraine",
        "stroke", "paralysis", "numbness", "tingling", "tremor", "alzheimer",
        "parkinson", "multiple sclerosis", "memory loss", "dizziness", "vertigo",
    ],
    # Orthopedics
    "ortho": [
        "bone", "joint", "fracture", "back pain", "spine", "knee", "hip",
        "shoulder", "arthritis", "muscle", "ligament", "tendon", "sports injury",
        "scoliosis", "osteoporosis", "cartilage",
    ],
    # Dermatology
    "dermat": [
        "skin", "rash", "acne", "eczema", "psoriasis", "hair loss", "nail",
        "allergy", "itching", "hives", "lesion", "mole", "melanoma", "dermatitis",
        "fungal infection", "wart",
    ],
    # Pediatrics
    "pediat": [
        "child", "baby", "infant", "toddler", "vaccination", "growth", "fever",
        "cough", "pediatric", "development", "childhood", "newborn",
    ],
    # Gynecology / Obstetrics
    "gyneco": [
        "pregnancy", "menstrual", "ovary", "uterus", "vaginal", "pelvic",
        "fertility", "menopause", "contraception", "cervical", "breast", "prenatal",
    ],
    "obstet": [
        "pregnancy", "labor", "delivery", "prenatal", "postnatal", "miscarriage",
        "maternal", "antenatal",
    ],
    # Ophthalmology
    "ophthal": [
        "eye", "vision", "sight", "glasses", "cataract", "glaucoma", "retina",
        "blurred vision", "cornea", "conjunctivitis", "dry eye", "strabismus",
    ],
    # ENT
    "ent": [
        "ear", "nose", "throat", "hearing", "sinusitis", "tonsil", "snoring",
        "allergy", "tinnitus", "nasal", "sore throat", "voice", "hoarseness",
    ],
    "otolaryn": [
        "ear", "nose", "throat", "hearing", "sinusitis", "tonsil",
    ],
    # Pulmonology
    "pulmon": [
        "lung", "breathing", "asthma", "copd", "pneumonia", "cough", "bronchitis",
        "tuberculosis", "respiratory", "shortness of breath", "oxygen", "sleep apnea",
    ],
    # Gastroenterology
    "gastro": [
        "stomach", "digestion", "bowel", "liver", "colon", "intestine", "acid reflux",
        "ulcer", "ibs", "crohn", "colitis", "abdominal pain", "nausea", "vomiting",
        "diarrhea", "constipation", "hepatitis", "gallbladder",
    ],
    # Endocrinology
    "endocrin": [
        "diabetes", "thyroid", "hormone", "insulin", "blood sugar", "adrenal",
        "obesity", "metabolic", "pituitary", "growth hormone",
    ],
    # Psychiatry / Psychology
    "psychiat": [
        "mental", "depression", "anxiety", "stress", "mood", "bipolar", "schizophrenia",
        "ocd", "ptsd", "panic", "therapy", "counseling", "insomnia", "suicidal",
    ],
    # Urology
    "urolog": [
        "kidney", "bladder", "urine", "urinary", "prostate", "uti", "incontinence",
        "kidney stone", "renal", "erectile",
    ],
    # Oncology
    "oncolog": [
        "cancer", "tumor", "chemotherapy", "radiation", "biopsy", "malignant",
        "lymphoma", "leukemia", "metastasis",
    ],
    # General / Family Medicine
    "general": [
        "fever", "cold", "flu", "fatigue", "checkup", "routine", "vaccination",
        "weight", "blood test", "general", "wellness",
    ],
    "family": [
        "fever", "cold", "flu", "fatigue", "checkup", "routine",
        "weight", "blood test", "general", "wellness",
    ],
}


def get_keywords_for_speciality(speciality: str) -> list:
    """
    Returns a list of related keywords for a given speciality string.
    Matches partial strings so 'Cardiologist' matches 'cardio' key.
    """
    if not speciality:
        return []
    speciality_lower = speciality.lower()
    matched_keywords = []
    for key, keywords in SPECIALITY_KEYWORDS.items():
        if key in speciality_lower:
            matched_keywords.extend(keywords)
    return matched_keywords


def check_reason_matches_speciality(reason: str, speciality: str) -> bool:
    """
    Returns True if the reason_for_visit appears related to the doctor's speciality.
    Returns True (no mismatch) if no keywords are found for the speciality (unknown speciality).
    """
    keywords = get_keywords_for_speciality(speciality)
    if not keywords:
        return True  # Unknown speciality — allow through
    reason_lower = reason.lower()
    return any(kw in reason_lower for kw in keywords)
