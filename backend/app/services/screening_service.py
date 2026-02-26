from sqlalchemy.orm import Session
from app.models.screening import Screening
from app.services.audit_service import log_action


def get_active_session(db: Session, patient_id: int):
    """
    Returns the active (incomplete) screening session for a patient.
    """
    return (
        db.query(Screening)
        .filter(
            Screening.patient_id == patient_id,
            Screening.is_complete == False
        )
        .first()
    )


def create_new_session(db: Session, patient_id: int):
    """
    Creates a new empty screening session.
    """
    screening = Screening(patient_id=patient_id)
    db.add(screening)
    db.commit()
    db.refresh(screening)
    return screening


def compute_dynamic_fusion(screening: Screening):
    """
    Computes final risk score using equal weighting
    based on available modality scores.
    """

    scores = []
    available = []

    if screening.handwriting_score is not None:
        scores.append(screening.handwriting_score)
        available.append("handwriting")

    if screening.speech_score is not None:
        scores.append(screening.speech_score)
        available.append("speech")

    if screening.gait_score is not None:
        scores.append(screening.gait_score)
        available.append("gait")

    if not scores:
        return None, None, None, None

    # Equal weighting (simple average)
    final_score = sum(scores) / len(scores)

    # Risk level classification
    if final_score < 0.35:
        risk_level = "Normal"
    elif final_score < 0.65:
        risk_level = "Moderate"
    else:
        risk_level = "High"

    modalities_present = ",".join(available)
    is_complete = len(available) == 3

    return final_score, risk_level, modalities_present, is_complete


def update_screening_session(
    db: Session,
    patient_id: int,
    modality: str,
    score: float,
    user_id: int
):
    """
    Updates (or creates) a screening session for a patient,
    recalculates fusion dynamically,
    and logs inference action.
    """

    # Get existing active session
    screening = get_active_session(db, patient_id)

    # If none exists, create new session
    if not screening:
        screening = create_new_session(db, patient_id)

    # Update modality score
    if modality == "handwriting":
        screening.handwriting_score = score
    elif modality == "speech":
        screening.speech_score = score
    elif modality == "gait":
        screening.gait_score = score
    else:
        raise ValueError("Invalid modality")

    # Recompute fusion
    final_score, risk_level, modalities_present, is_complete = compute_dynamic_fusion(screening)

    screening.final_risk_score = final_score
    screening.risk_level = risk_level
    screening.modalities_present = modalities_present
    screening.is_complete = is_complete

    db.commit()
    db.refresh(screening)

    # 🔥 Log every modality inference
    log_action(
        db=db,
        user_id=user_id,
        action="INFERENCE",
        entity="Screening",
        entity_id=screening.id
    )

    return screening