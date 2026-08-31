import psycopg2
from app.core.config import settings

try:
    conn = psycopg2.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        database=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASS
    )
    cur = conn.cursor()
except Exception as err:
    print(f"Warning: Database connection failed ({err}). DB operations will be unavailable.")
    conn = None
    cur = None

def get_cursor():
    """Dependency / accessor for DB cursor."""
    return cur
