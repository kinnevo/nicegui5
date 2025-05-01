from utilities.database import PostgresAdapter
from datetime import datetime, timezone
import uuid

create_users_table_sql = """
                    CREATE TABLE IF NOT EXISTS sv_users (
                        id SERIAL PRIMARY KEY,
                        username TEXT NOT NULL,
                        session_id TEXT NOT NULL UNIQUE,
                        group_id TEXT NOT NULL,
                        last_active TIMESTAMP,
                        status TEXT DEFAULT 'Idle',
                        logged BOOLEAN DEFAULT FALSE
                    );
                """

db = None  # Initialize as None

def initialize_user_db():
    global db
    db = PostgresAdapter('svusers', create_users_table_sql)

def generate_session_id() -> str:
    """Generate a unique session ID."""
    return str(uuid.uuid4())

def insert_user(username: str, session_id: str, group_id: str, last_active: str, logged: bool) -> bool:
    """
    Insert a new user into the database.
    Returns status of the operation.
    """
    if db is None:  
        raise RuntimeError("Database not initialized")
    conn = db.connection_pool.getconn()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO sv_users (username, session_id, group_id, last_active, logged)
                VALUES (%s, %s, %s, %s, %s)
            """, (username, session_id, group_id, last_active, logged))
            conn.commit()
            return True
    finally:
        db.connection_pool.putconn(conn)

def logout_user(session_id: str) -> bool:
    """
    Logout user, updating their status and logged flag.
    Returns success status.
    """
    if db is None:
        raise RuntimeError("Database not initialized")
    conn = db.connection_pool.getconn()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE sv_users 
                SET status = 'Idle',
                    logged = false,
                    last_active = %s
                WHERE session_id = %s
            """, (datetime.now(timezone.utc), session_id))
            conn.commit()
            return cursor.rowcount > 0
    finally:
        db.connection_pool.putconn(conn)

def get_all_users():
    """Get all users (returns list of dicts)."""
    # You may want to add this to PostgresAdapter if not present
    if db is None:
        raise RuntimeError("Database not initialized")
    conn = db.connection_pool.getconn()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM sv_users ORDER BY id")
            rows = cursor.fetchall()
            return [dict(zip([desc[0] for desc in cursor.description], row)) for row in rows]
        
    finally:
        db.connection_pool.putconn(conn)

def get_all_users_logged_in():
    """Get all users (returns list of dicts)."""
    # You may want to add this to PostgresAdapter if not present
    if db is None:
        raise RuntimeError("Database not initialized")
    conn = db.connection_pool.getconn()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM sv_users WHERE logged = true ORDER BY id")
            rows = cursor.fetchall()
            return [dict(zip([desc[0] for desc in cursor.description], row)) for row in rows]
    finally:
        db.connection_pool.putconn(conn)        

def remove_user(session_id: str) -> bool:
    """Remove a user by session_id."""
    if db is None:
        raise RuntimeError("Database not initialized")
    conn = db.connection_pool.getconn()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM sv_users WHERE session_id = %s", (session_id,))
            conn.commit()
            return cursor.rowcount > 0
    finally:
        db.connection_pool.putconn(conn)

def user_logged_in(username: str) -> bool:  
    """Check if a user is logged in."""
    if db is None:
        raise RuntimeError("Database not initialized")

    conn = db.connection_pool.getconn()
    print("Fifth")
    try:
        print(f"Sixth - checking if user {username} is logged in")
        with conn.cursor() as cursor:
            cursor.execute("SELECT logged FROM sv_users WHERE username = %s", (username,))
            rows = cursor.fetchall()
            if not rows:
                print(f"false {rows}")
                return False  # User doesn't exist
            print(f"true {rows}")
            return rows[0][0]  # Return logged status
    finally:
        print("Seventh")
        db.connection_pool.putconn(conn)

def set_user_logout(username: str, session_id: str) -> bool:
    """Set a user as logged out."""
    if db is None:
        raise RuntimeError("Database not initialized")
    conn = db.connection_pool.getconn()
    try:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE sv_users SET logged = FALSE, last_active = %s, status = 'Idle' WHERE username = %s AND session_id = %s", (datetime.now(timezone.utc), username, session_id))
            conn.commit()
            print(f"User {username} logged out")
            return cursor.rowcount > 0
    finally:
        db.connection_pool.putconn(conn)

def update_user_status(username: str, session_id: str) -> bool:
    """Update user's logged status to False and status to Idle."""
    if db is None:
        raise RuntimeError("Database not initialized")
    conn = db.connection_pool.getconn()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE sv_users 
                SET logged = false, status = 'Idle'
                WHERE username = %s AND session_id = %s
            """, (username, session_id))
            conn.commit()
            return cursor.rowcount > 0
    finally:
        db.connection_pool.putconn(conn)
