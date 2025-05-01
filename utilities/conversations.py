import os
from datetime import datetime
from typing import Optional, Dict, Any
from nicegui import app
import psycopg2
from psycopg2.extras import DictCursor
from psycopg2.pool import SimpleConnectionPool
from dotenv import load_dotenv

load_dotenv()

class UserDB:
    def __init__(self):
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
        """Initialize the database with the sv_conversations table."""
        conn = self.connection_pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS sv_conversations (
                        session_id VARCHAR(255) PRIMARY KEY,
                        username VARCHAR(255) NOT NULL,
                        save_time TIMESTAMP NOT NULL,
                        visits INTEGER NOT NULL,
                        conversation_history TEXT
                    )
                ''')
            conn.commit()
        finally:
            self.connection_pool.putconn(conn)

    def create_conversation(self, session_id: str, username: str, conversation_history: str, visits: int) -> bool:
        """Create a new conversation record."""
        conn = self.connection_pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute('''
                    INSERT INTO sv_conversations (session_id, username, save_time, conversation_history, visits)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (session_id, username, datetime.now(), conversation_history, visits))
            conn.commit()
            return True
        except psycopg2.IntegrityError:
            return False
        finally:
            self.connection_pool.putconn(conn)

    def update_conversation(self, session_id: str, conversation_history: str, visits: int) -> bool:
        """Update an existing conversation with new history."""
        conn = self.connection_pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute('''
                    UPDATE sv_conversations 
                    SET conversation_history = %s, visits = %s
                    WHERE session_id = %s
                ''', (conversation_history, visits, session_id))
            conn.commit()
            return True
        except psycopg2.Error:
            return False
        finally:
            self.connection_pool.putconn(conn)

    def get_conversation(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation details by session_id."""
        conn = self.connection_pool.getconn()
        try:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute('SELECT * FROM sv_conversations WHERE session_id = %s', (session_id,))
                result = cursor.fetchone()
                if result:
                    return dict(result)
            return None
        finally:
            self.connection_pool.putconn(conn)

# Create a global instance
user_db = UserDB()

def save_db():
    session_id = app.storage.browser['session_id']
    username = app.storage.browser.get('username', 'Unknown User')
    conversation = str(app.storage.browser['conversation_history'])
    visits = app.storage.browser['visits']
    # Try to update first
    if not user_db.update_conversation(session_id, conversation, visits):
        # If update fails, create new conversation
        user_db.create_conversation(session_id, username, conversation, visits) 

def get_conversation(session_id: str) -> Optional[Dict[str, Any]]:
    """Get conversation details by session_id."""
    conn = user_db.connection_pool.getconn()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute('SELECT * FROM sv_conversations WHERE session_id = %s', (session_id,))
            result = cursor.fetchone()
            if result:
                return dict(result)
            return None
    finally:
        user_db.connection_pool.putconn(conn)
        