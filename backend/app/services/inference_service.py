# app/services/inference_service.py

def run_handwriting_model():
    # TODO: Replace with real model loading + inference
    return 0.42


def run_speech_model():
    # TODO: Replace with real model loading + inference
    return 0.38


def run_gait_model():
    # TODO: Replace with real model loading + inference
    return 0.67


def compute_final_risk(hw_score, speech_score, gait_score):
    """
    Weighted Late Fusion:
    p_final = 0.30*p_HW + 0.20*p_VOICE + 0.50*p_GAIT
    """

    final_score = (
        0.30 * hw_score +
        0.20 * speech_score +
        0.50 * gait_score
    )

    if final_score < 0.35:
        risk_level = "Normal"
    elif final_score < 0.65:
        risk_level = "Moderate"
    else:
        risk_level = "High"

    return final_score, risk_level


def run_full_inference():
    hw = run_handwriting_model()
    speech = run_speech_model()
    gait = run_gait_model()

    final_score, risk_level = compute_final_risk(hw, speech, gait)

    return {
        "handwriting_score": hw,
        "speech_score": speech,
        "gait_score": gait,
        "final_risk_score": final_score,
        "risk_level": risk_level
    }
