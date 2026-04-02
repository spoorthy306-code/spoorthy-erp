# Single authoritative Base — used by Alembic migrations and all model files.
from backend.app.models.models import Base

# Alembic target metadata is sourced from backend.app.models.models.Base.
# Avoid importing legacy modules here because they redefine several table names
# and trigger InvalidRequestError during migration execution.
