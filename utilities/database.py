# import pytz

# # Set up San Francisco (Pacific Time) timezone
# sf_timezone = pytz.timezone('America/Los_Angeles')

# def get_sf_time():
#     """Get current time in San Francisco timezone"""
#     # Create a timezone-aware UTC datetime and then convert it to SF timezone
#     return datetime.now(pytz.utc).astimezone(sf_timezone)


import os
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from dotenv import load_dotenv

load_dotenv()

def create_database():
    """Create the visit_sv database if it doesn't exist."""
    # Connect to default postgres database first
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST'),
        database='postgres',  # Connect to default postgres db
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        port=os.getenv('POSTGRES_PORT', '5432')
    )
    conn.autocommit = True  # Required for creating database

    new_database = os.getenv('POSTGRES_DB')
    try:
        with conn.cursor() as cursor:
            # Check if database exists
            cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (new_database,))
            exists = cursor.fetchone()
            
            if not exists:
                cursor.execute(f'CREATE DATABASE {new_database}')
                print(f"Database '{new_database}' created successfully")
            else:
                print(f"Database '{new_database}' already exists")
    except psycopg2.Error as e:
        print(f"Error creating database: {e}")
    finally:
        conn.close()

class PostgresAdapter:
    def __init__(self, tablename, create_table_sql):
        self.tablename = tablename
        self.create_table_sql = create_table_sql
        self.connection_pool = self._create_connection_pool()
        self._init_db()

    def _create_connection_pool(self):
        """Create a connection pool for PostgreSQL."""
        return SimpleConnectionPool(
            1,  # minconn
            20,  # maxconn
            host=os.getenv('POSTGRES_HOST'),
            database=os.getenv('POSTGRES_DB'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            port=os.getenv('POSTGRES_PORT', '5432')
        )

    def __del__(self):
        """Clean up the connection pool when the object is destroyed."""
        if hasattr(self, 'connection_pool'):
            self.connection_pool.closeall()

    def _init_db(self):
        """Initialize the database with the required tables."""
        conn = self.connection_pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute(self.create_table_sql)
            conn.commit()
        finally:
            self.connection_pool.putconn(conn)
