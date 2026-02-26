from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Import all models here for Alembic to detect them
from app.models import user
from app.models import patient
from app.models import screening
from app.models import audit_log
