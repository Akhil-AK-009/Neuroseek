def generate_screening_report(result, patient_id, screening_id):

    score = result["final_risk_score"]
    level = result["risk_level"]

    if level == "Normal":
        interpretation = "No significant Parkinsonian indicators detected."

    elif level == "Moderate":
        interpretation = "Moderate motor abnormality risk detected. Clinical follow-up recommended."

    else:
        interpretation = "High Parkinsonian motor abnormality detected. Neurological evaluation recommended."

    report = {

        "patient_id": patient_id,

        "screening_id": screening_id,

        "overall_risk": {
            "score": score,
            "level": level
        },

        "modalities": {

            "handwriting": result["handwriting_score"],

            "speech": result["speech_score"],

            "gait": result["gait_score"]
        },

        "interpretation": interpretation
    }

    return report