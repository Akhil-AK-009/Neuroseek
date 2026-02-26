from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog


def log_action(
    db: Session,
    user_id: int,
    action: str,
    entity: str,
    entity_id: int | None = None
):
    """
    Create an audit log entry.

    :param db: Database session
    :param user_id: ID of the user performing the action
    :param action: Action performed (CREATE, UPDATE, DELETE, VIEW, INFERENCE)
    :param entity: Entity name (Patient, Screening, User)
    :param entity_id: ID of the affected record
    """

    audit_entry = AuditLog(
        user_id=user_id,
        action=action,
        entity=entity,
        entity_id=entity_id
    )

    db.add(audit_entry)
    db.commit()
