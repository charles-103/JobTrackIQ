"""
app.models package initializer.

All SQLAlchemy models must be imported here so Alembic can discover them
when running autogenerate migrations.

Use absolute imports only.
"""

from app.models.application import Application  # noqa: F401
from app.models.event import Event  # noqa: F401
from app.models.company_index import CompanyIndex  # noqa: F401
from app.models.role import Role  # noqa: F401
from app.models.user import User  # noqa: F401