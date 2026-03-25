"""
Medical utilities: summarization, report generation, symptom-disease mapping.
For educational/demo purposes only - NOT medical advice.
"""

import nltk

# Ensure TextBlob/NLTK corpora are available (punkt for sentence tokenization)
try:
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    nltk.download("punkt_tab", quiet=True)
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt", quiet=True)

from textblob import TextBlob
from datetime import datetime

# Symptom -> Possible conditions (simplified mapping for demo - NOT medical diagnosis)
SYMPTOM_DISEASE_MAP = {
    "headache": [
        "Migraine",
        "Tension headache",
        "Cluster headache",
        "Sinusitis",
        "Hypertension",
        "Dehydration",
        "Subarachnoid hemorrhage (if sudden severe)",
    ],
    "migraine": ["Migraine with aura", "Migraine without aura", "Chronic migraine"],
    "seizure": ["Epilepsy", "Febrile seizure", "Syncope", "Metabolic causes"],
    "numbness": ["Stroke", "Transient ischemic attack", "Multiple sclerosis", "Peripheral neuropathy"],
    "tingling": ["Peripheral neuropathy", "Carpal tunnel syndrome", "Vitamin B12 deficiency", "Multiple sclerosis"],
    "tremor": ["Essential tremor", "Parkinson disease", "Hyperthyroidism", "Drug-induced tremor"],
    "memory loss": ["Alzheimer disease", "Mild cognitive impairment", "Depression", "Vitamin B12 deficiency"],
    "confusion": ["Delirium", "Encephalopathy", "Infection", "Metabolic disturbance"],
    "slurred speech": ["Stroke", "TIA", "Bell palsy", "Intoxication"],
    "vision loss": ["Stroke", "Optic neuritis", "Glaucoma", "Retinal detachment"],
    "double vision": ["Cranial nerve palsy", "Myasthenia gravis", "Stroke"],
    "neck stiffness": ["Meningitis", "Cervical spondylosis", "Muscle strain"],
    "weakness one side": ["Stroke", "TIA", "Focal seizure"],
    "facial droop": ["Stroke", "Bell palsy", "Facial nerve palsy"],
    "parkinson": ["Parkinson disease", "Parkinsonism", "Drug-induced parkinsonism"],
    "epilepsy": ["Generalized epilepsy", "Focal epilepsy", "Status epilepticus"],
    "multiple sclerosis": ["Relapsing-remitting MS", "Primary progressive MS", "Secondary progressive MS"],
    "neuropathy": ["Diabetic neuropathy", "Peripheral neuropathy", "Vitamin deficiency neuropathy"],
    "dizziness": [
        "Benign paroxysmal positional vertigo",
        "Vestibular neuritis",
        "Inner ear issue",
        "Dehydration",
        "Low blood pressure",
        "Anemia",
    ],
    "fever": ["Viral infection", "Bacterial infection", "Flu", "COVID-19", "UTI"],
    "cough": ["Common cold", "Bronchitis", "Asthma", "COVID-19", "Pneumonia", "Allergies"],
    "sore throat": ["Pharyngitis", "Strep throat", "Common cold", "Allergies", "Flu"],
    "fatigue": ["Anemia", "Thyroid issues", "Sleep disorder", "Chronic fatigue", "Depression"],
    "nausea": ["Gastroenteritis", "Food poisoning", "Migraine", "Pregnancy", "Anxiety"],
    "vomiting": ["Gastroenteritis", "Food poisoning", "Migraine", "Motion sickness"],
    "diarrhea": ["Gastroenteritis", "Food poisoning", "IBS", "Viral infection"],
    "chest pain": [
        "GERD",
        "Angina pectoris",
        "Acute coronary syndrome",
        "Pericarditis",
        "Muscle strain",
        "Heart-related - seek urgent care",
    ],
    "chest tightness": ["Angina", "Coronary artery disease", "Anxiety", "Asthma", "GERD"],
    "palpitation": ["Atrial fibrillation", "Anxiety", "Hyperthyroidism", "Premature ventricular contractions"],
    "heart racing": ["Tachycardia", "Atrial fibrillation", "Anxiety", "Hyperthyroidism"],
    "swollen legs": ["Congestive heart failure", "Venous insufficiency", "Kidney disease", "Deep vein thrombosis"],
    "ankle swelling": ["Congestive heart failure", "Venous insufficiency", "Kidney disease"],
    "high blood pressure": ["Hypertension", "Secondary hypertension", "White-coat hypertension"],
    "hypertension": ["Essential hypertension", "Secondary hypertension", "Renovascular hypertension"],
    "heart murmur": ["Valvular heart disease", "Mitral regurgitation", "Aortic stenosis", "Innocent murmur"],
    "irregular heartbeat": ["Atrial fibrillation", "Atrial flutter", "Premature beats", "Ventricular arrhythmia"],
    "angina": ["Stable angina", "Unstable angina", "Coronary artery disease", "Microvascular angina"],
    "breathing": ["Asthma", "Anxiety", "Pneumonia", "Allergies", "COPD"],
    "shortness of breath": [
        "Asthma",
        "Pneumonia",
        "Heart failure",
        "Pulmonary embolism",
        "Anxiety",
        "COPD",
    ],
    "back pain": ["Muscle strain", "Lumbar disc herniation", "Spinal stenosis", "Kidney issue"],
    "sciatica": ["Lumbar radiculopathy", "Herniated disc", "Spinal stenosis", "Piriformis syndrome"],
    "knee pain": ["Osteoarthritis", "Meniscal tear", "Patellofemoral pain", "Ligament sprain"],
    "hip pain": ["Hip osteoarthritis", "Trochanteric bursitis", "Labral tear", "Avascular necrosis"],
    "shoulder pain": ["Rotator cuff tear", "Adhesive capsulitis", "Tendinitis", "AC joint injury"],
    "ankle pain": ["Ankle sprain", "Achilles tendinitis", "Osteoarthritis", "Gout"],
    "wrist pain": ["Carpal tunnel syndrome", "Tendinitis", "Arthritis", "Sprain"],
    "fracture": ["Bone fracture (needs imaging)", "Osteoporosis-related", "Stress fracture"],
    "bone pain": ["Osteoporosis", "Metastatic disease", "Osteomyelitis", "Fracture"],
    "arthritis": ["Osteoarthritis", "Rheumatoid arthritis", "Psoriatic arthritis", "Gout"],
    "joint swelling": ["Rheumatoid arthritis", "Gout", "Septic arthritis", "Osteoarthritis"],
    "stiff joints": ["Rheumatoid arthritis", "Osteoarthritis", "Ankylosing spondylitis"],
    "sprain": ["Ligament sprain", "Ankle sprain", "Wrist sprain"],
    "elbow pain": ["Tennis elbow", "Golfer elbow", "Olecranon bursitis", "Arthritis"],
    "neck pain": ["Cervical spondylosis", "Muscle strain", "Cervical radiculopathy", "Whiplash"],
    "scoliosis": ["Idiopathic scoliosis", "Degenerative scoliosis", "Neuromuscular scoliosis"],
    "osteoporosis": ["Primary osteoporosis", "Postmenopausal osteoporosis", "Glucocorticoid-induced"],
    "torn ligament": ["ACL tear", "Ankle ligament tear", "Collateral ligament injury"],
    "stomach pain": ["Gastritis", "IBS", "Appendicitis", "Indigestion"],
    "abdominal pain": ["Gastritis", "IBS", "Appendicitis", "Indigestion", "UTI"],
    "joint pain": ["Osteoarthritis", "Rheumatoid arthritis", "Gout", "Bursitis", "Lupus"],
    "rash": ["Allergic reaction", "Eczema", "Contact dermatitis", "Viral rash"],
    "insomnia": ["Stress", "Sleep disorder", "Anxiety", "Caffeine"],
    "anxiety": ["Anxiety disorder", "Stress", "Thyroid issue", "Caffeine"],
    "depression": ["Depression", "Thyroid issue", "Vitamin D deficiency"],
    "runny nose": ["Common cold", "Allergies", "Sinusitis", "Flu"],
    "congestion": ["Common cold", "Allergies", "Sinusitis"],
    "body ache": ["Flu", "Viral infection", "Fibromyalgia", "Dehydration"],
    "chills": ["Infection", "Flu", "Fever", "Malaria"],
    "sweating": ["Infection", "Fever", "Anxiety", "Thyroid"],
    "loss of appetite": ["Infection", "Depression", "Digestive issue", "Medication side effect"],
    "weight loss": ["Hyperthyroidism", "Diabetes", "Depression", "Malabsorption"],
    "swelling": ["Allergic reaction", "Injury", "Infection", "Edema"],
    "weakness": ["Anemia", "Dehydration", "Infection", "Low blood sugar"],
}

# Condition/symptom -> Suggested medicines (reference only - consult doctor/pharmacist)
MEDICINE_MAP = {
    "headache": ["Paracetamol", "Ibuprofen", "Aspirin"],
    "fever": ["Paracetamol", "Ibuprofen"],
    "cough": ["Dextromethorphan", "Guaifenesin", "Honey + warm fluids"],
    "sore throat": ["Throat lozenges", "Paracetamol", "Warm salt gargle"],
    "fatigue": ["Rest", "Iron supplement (if anemic)", "B vitamins"],
    "nausea": ["Ginger", "Ondansetron (if prescribed)", "Small bland meals"],
    "vomiting": ["Rehydration solution", "Ginger", "Avoid solid food initially"],
    "diarrhea": ["Oral rehydration salts", "Loperamide (adults)", "Bland diet"],
    "runny nose": ["Antihistamines", "Decongestants", "Saline nasal spray"],
    "congestion": ["Pseudoephedrine", "Saline spray", "Steam inhalation"],
    "body ache": ["Paracetamol", "Ibuprofen", "Rest"],
    "back pain": ["Ibuprofen", "Paracetamol", "Topical pain relief", "Rest"],
    "joint pain": ["Ibuprofen", "Paracetamol", "Topical NSAIDs"],
    "stomach pain": ["Antacids", "Avoid trigger foods", "Consult if severe"],
    "abdominal pain": ["Antacids", "Peppermint tea", "Consult if severe"],
    "rash": ["Antihistamines", "Topical hydrocortisone", "Avoid irritants"],
    "insomnia": ["Sleep hygiene", "Melatonin (OTC)", "Avoid caffeine"],
    "allergies": ["Antihistamines (Cetirizine/Loratadine)", "Nasal spray"],
    "flu": ["Paracetamol", "Rest", "Fluids", "Oseltamivir (if prescribed)"],
    "common cold": ["Paracetamol", "Decongestants", "Vitamin C", "Rest"],
    "sinusitis": ["Decongestants", "Nasal irrigation", "Paracetamol"],
    "dehydration": ["Oral rehydration solution", "Water", "Electrolytes"],
    "acid reflux": ["Antacids", "Proton pump inhibitors (OTC)", "Avoid trigger foods"],
    "migraine": ["Paracetamol", "Ibuprofen", "Rest in dark room", "Triptans (prescription)"],
}


def summarize_text(text: str, max_sentences: int = 5) -> str:
    """Create extractive summary from conversation text."""
    if not text.strip():
        return ""
    blob = TextBlob(text)
    sentences = [str(s) for s in blob.sentences if len(str(s).strip()) > 10]
    if not sentences:
        return text[:500] + "..." if len(text) > 500 else text
    # Simple approach: take first and last sentences + key content
    key_sentences = sentences[:2] + sentences[-2:] if len(sentences) > 4 else sentences[:max_sentences]
    return " ".join(key_sentences)


def suggest_medicines(text: str) -> list:
    """Suggest possible medicines based on symptoms. Reference only - consult doctor/pharmacist."""
    text_lower = text.lower().strip()
    found = set()
    for symptom, meds in MEDICINE_MAP.items():
        if symptom in text_lower:
            for m in meds:
                found.add(m)
    return list(found)[:10]


def generate_medical_report(
    conversation_text: str,
    suggested_conditions: list,
    suggested_medicines: list = None,
    *,
    patient_name: str = "",
    patient_age: str = "",
    patient_bp: str = "",
) -> str:
    """Generate a structured medical report from conversation."""
    summary = summarize_text(conversation_text, max_sentences=6)
    date_str = datetime.now().strftime("%B %d, %Y")
    if suggested_medicines is None:
        suggested_medicines = suggest_medicines(conversation_text)

    pn = patient_name.strip() or "—"
    pa = patient_age.strip() or "—"
    pb = patient_bp.strip() or "—"

    conditions_block = chr(10).join(f'• {c}' for c in suggested_conditions) if suggested_conditions else '• No specific conditions identified from symptoms mentioned.'
    medicines_block = chr(10).join(f'• {m}' for m in suggested_medicines) if suggested_medicines else '• Consult a doctor or pharmacist for medication advice.'

    report = f"""
═══════════════════════════════════════════════════════════
                    MEDICAL CONSULTATION REPORT
                    Generated: {date_str}
═══════════════════════════════════════════════════════════

👤 PATIENT DETAILS
───────────────────────────────────────────────────────────
Patient name: {pn}
Age: {pa}
Blood pressure (BP): {pb}

📋 CONVERSATION SUMMARY
───────────────────────────────────────────────────────────
{summary}

⚠️ POSSIBLE CONDITIONS TO CONSIDER (AI-assisted, for reference only)
───────────────────────────────────────────────────────────
{conditions_block}

💊 SUGGESTED MEDICINES (AI — reference only, not a prescription)
───────────────────────────────────────────────────────────
{medicines_block}

💉 PRESCRIBED MEDICATIONS (doctor — add drug name, dose, route, frequency, duration)
───────────────────────────────────────────────────────────
• 

📌 RECOMMENDATIONS
───────────────────────────────────────────────────────────
• This report is AI-generated and for informational purposes only.
• Always consult a qualified healthcare professional for diagnosis.
• Do not take any medicine without consulting a doctor or pharmacist.

═══════════════════════════════════════════════════════════
"""
    return report.strip()


def generate_report_pdf(report_text: str) -> bytes:
    """Generate PDF bytes from report text."""
    from fpdf import FPDF

    # Clean text for PDF - ASCII only for default font (bullet, box chars etc)
    clean = (
        report_text.replace("═", "=").replace("─", "-").replace("•", "-")
    )
    clean = "".join(c if ord(c) < 128 else " " for c in clean)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)
    pdf.set_auto_page_break(auto=True, margin=15)
    # Use explicit width to avoid fpdf2 "not enough horizontal space" bug
    w = pdf.epw  # effective page width

    for line in clean.split("\n"):
        line = line.strip().replace("\r", "")
        if not line:
            pdf.ln(4)
            continue
        pdf.multi_cell(w=w, h=6, txt=line)
    out = pdf.output(dest="S")
    return bytes(out)  # Ensure bytes for Streamlit download_button


def suggest_diseases(text: str) -> list:
    """Suggest possible conditions based on symptoms mentioned. Demo only - NOT medical advice."""
    text_lower = text.lower().strip()
    found = set()
    for symptom, conditions in SYMPTOM_DISEASE_MAP.items():
        if symptom in text_lower:
            for c in conditions:
                found.add(c)
    return list(found)[:16]  # Limit suggestions (heart / neuro / ortho expanded)
