import os

# Database URL — override with CRITERIAMETER_DATABASE_URL for PostgreSQL.
# SQLite default creates criteriameter.db in the backend working directory.
DATABASE_URL: str = os.getenv(
    "CRITERIAMETER_DATABASE_URL",
    "sqlite:///./criteriameter.db",
)
