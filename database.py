import os
import psycopg2
from psycopg2 import OperationalError
from dotenv import load_dotenv


# .env файлын жүктеу
load_dotenv()

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "options": "-c client_encoding=UTF8",
}


def _safe_text(value):
    if value is None:
        return None
    if isinstance(value, str):
        return value.encode("utf-8", errors="replace").decode("utf-8")
    return str(value)


def get_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.set_client_encoding("UTF8")
        return conn
    except OperationalError as e:
        print("❌ Database connection error:", e)
        raise


# ✅ Қолданушы қосу
def add_user(user_id, username, first_name):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        safe_username = _safe_text(username)
        safe_first_name = _safe_text(first_name)

        cursor.execute("""
            INSERT INTO users (user_id, username, first_name, joined_at, last_activity)
            VALUES (%s, %s, %s, NOW(), NOW())
            ON CONFLICT (user_id) DO NOTHING;
        """, (user_id, safe_username, safe_first_name))

        conn.commit()
        cursor.close()

    except Exception as e:
        print("❌ add_user error:", e)

    finally:
        if conn:
            conn.close()


# ✅ Активтілік жаңарту
def update_activity(user_id):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE users
            SET last_activity = NOW(),
                messages_count = messages_count + 1
            WHERE user_id = %s;
        """, (user_id,))

        conn.commit()
        cursor.close()

    except Exception as e:
        print("❌ update_activity error:", e)

    finally:
        if conn:
            conn.close()


# ✅ Толық статистика (онлайнмен бірге)
def get_full_stats():
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Жалпы қолданушылар
        cursor.execute("SELECT COUNT(*) FROM users;")
        total_users = cursor.fetchone()[0]

        # 24 сағат активті
        cursor.execute("""
            SELECT COUNT(*) FROM users
            WHERE last_activity >= NOW() - INTERVAL '1 day';
        """)
        active_24h = cursor.fetchone()[0]

        # Қазір онлайн (соңғы 5 минут)
        cursor.execute("""
            SELECT COUNT(*) FROM users
            WHERE last_activity >= NOW() - INTERVAL '5 minutes';
        """)
        online_now = cursor.fetchone()[0]

        # Барлық хабарламалар
        cursor.execute("""
            SELECT COALESCE(SUM(messages_count), 0) FROM users;
        """)
        total_messages = cursor.fetchone()[0]

        cursor.close()

        return total_users, active_24h, online_now, total_messages

    except Exception as e:
        print("❌ get_full_stats error:", e)
        return 0, 0, 0, 0

    finally:
        if conn:
            conn.close()