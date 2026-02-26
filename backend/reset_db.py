"""Reset database script"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from app.core.config import settings

# Parse database URL
db_url = settings.DATABASE_URL
# postgresql://postgres:postgres@localhost:5432/gist_oms
parts = db_url.replace('postgresql://', '').split('@')
user_pass = parts[0].split(':')
host_db = parts[1].split('/')
host_port = host_db[0].split(':')

user = user_pass[0]
password = user_pass[1]
host = host_port[0]
port = host_port[1]
database = host_db[1]

print(f"Connecting to PostgreSQL to reset database: {database}")

# Connect to PostgreSQL server (not to specific database)
conn = psycopg2.connect(
    user=user,
    password=password,
    host=host,
    port=port,
    database='postgres'
)
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cursor = conn.cursor()

# Drop and recreate database
try:
    print(f"Dropping database {database}...")
    cursor.execute(f"DROP DATABASE IF EXISTS {database}")
    print(f"Creating database {database}...")
    cursor.execute(f"CREATE DATABASE {database}")
    print("✓ Database reset successfully!")
except Exception as e:
    print(f"Error: {e}")
finally:
    cursor.close()
    conn.close()

# Now initialize the database
print("\nInitializing database with tables and default data...")
from app.db.init_db import init_db
init_db()
print("\n✓ Database initialization complete!")
