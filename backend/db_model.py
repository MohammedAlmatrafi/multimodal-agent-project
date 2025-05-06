from datetime import datetime, timedelta
import sqlite3
from uuid import uuid4
from typing import List


def init_db(db_path="chat.db"):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        )

        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS chats (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """
        )

        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT,
            role TEXT,
            content TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        )

        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS video_transcripts (
            chat_id TEXT,
            video_url TEXT,
            transcript TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        )

        conn.commit()
        print("✅ Database initialized successfully.")


init_db()


def create_user_if_not_exist(user_id: str):
    with sqlite3.connect("chat.db") as conn:
        cursor = conn.execute("SELECT 1 FROM users WHERE id = ?", (user_id,))
        if not cursor.fetchone():
            conn.execute("INSERT INTO users (id) VALUES (?)", (user_id,))
            conn.commit()


def create_new_chat(user_id: str) -> str:
    chat_id = str(uuid4())
    with sqlite3.connect("chat.db") as conn:
        conn.execute(
            "INSERT INTO chats (id, user_id) VALUES (?, ?)", (chat_id, user_id)
        )
        conn.commit()
    return chat_id


def get_user_chats(user_id: str) -> dict:
    query = """
    SELECT 
        c.id AS chat_id,
        c.created_at AS created_at,
        m.content AS first_user_message
    FROM chats c
    JOIN (
        SELECT 
            chat_id,
            content,
            ROW_NUMBER() OVER (PARTITION BY chat_id ORDER BY timestamp ASC) AS rn
        FROM messages
        WHERE role = 'user'
    ) m ON c.id = m.chat_id AND m.rn = 1
    WHERE c.user_id = ?
    ORDER BY c.created_at DESC
    """
    with sqlite3.connect("chat.db") as conn:
        cursor = conn.execute(query, (user_id,))
        results = cursor.fetchall()
        return {
            "chats": [
                {
                    "chat_id": row[0],
                    "created_at": (
                        (
                            datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S")
                            + timedelta(hours=3)
                        ).strftime("%Y-%m-%d %H:%M:%S")
                        if row[1]
                        else None
                    ),
                    "first_message": row[2],
                }
                for row in results
            ]
        }


def save_message(chat_id: str, role: str, content: str):
    with sqlite3.connect("chat.db") as conn:
        conn.execute(
            "INSERT INTO messages (chat_id, role, content) VALUES (?, ?, ?)",
            (chat_id, role, content),
        )
        conn.commit()


def get_chat_history(chat_id: str) -> List[dict]:
    # Returns [{'role': 'user', 'content': '...'}, ...]
    with sqlite3.connect("chat.db") as conn:
        cursor = conn.execute(
            "SELECT role, content, id FROM messages WHERE chat_id = ? ORDER BY timestamp",
            (chat_id,),
        )
        return [
            {"role": row[0], "content": row[1], "id": row[2]}
            for row in cursor.fetchall()
        ]
