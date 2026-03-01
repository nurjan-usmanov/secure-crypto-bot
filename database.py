# import os
# import psycopg2
# from psycopg2 import OperationalError
# from dotenv import load_dotenv


# # .env файлын жүктеу
# load_dotenv()

# DB_CONFIG = {
#     "dbname": os.getenv("DB_NAME"),
#     "user": os.getenv("DB_USER"),
#     "password": os.getenv("DB_PASSWORD"),
#     "host": os.getenv("DB_HOST"),
#     "port": os.getenv("DB_PORT"),
#     "options": "-c client_encoding=UTF8",
# }

# def _safe_text(value):
#     if value is None:
#         return ""
#     # Мәтінді тазалап, UTF-8 форматына келтіру
#     text = str(value)
#     return text.encode('utf-8', errors='ignore').decode('utf-8')

# def get_connection():
#     try:
#         conn = psycopg2.connect(
#             dbname=os.getenv("DB_NAME"),
#             user=os.getenv("DB_USER"),
#             password=os.getenv("DB_PASSWORD"),
#             host=os.getenv("DB_HOST"),
#             port=os.getenv("DB_PORT"),
#             client_encoding='UTF8', # Тікелей осында көрсету
#             connect_timeout=10
#         )
#         return conn
#     except OperationalError as e:
#         print("❌ Database connection error:", e)
#         raise


# # ✅ Қолданушы қосу
# def add_user(user_id, username, first_name):
#     conn = None
#     try:
#         conn = get_connection()
#         cursor = conn.cursor()

#         # Символдарды тазалау (NBSP таңбасын жою)
#         safe_username = _safe_text(username).replace('\xa0', ' ')
#         safe_first_name = _safe_text(first_name).replace('\xa0', ' ')

#         cursor.execute("""
#             INSERT INTO users (user_id, username, first_name, joined_at, last_activity)
#             VALUES (%s, %s, %s, NOW(), NOW())
#             ON CONFLICT (user_id) DO NOTHING;
#         """, (user_id, safe_username, safe_first_name))

#         conn.commit()
#         cursor.close()
#     except Exception as e:
#         print(f"❌ add_user error: {e}")
#     finally:
#         if conn: conn.close()


# # ✅ Активтілік жаңарту
# def update_activity(user_id):
#     conn = None
#     try:
#         conn = get_connection()
#         cursor = conn.cursor()

#         cursor.execute("""
#             UPDATE users
#             SET last_activity = NOW(),
#                 messages_count = messages_count + 1
#             WHERE user_id = %s;
#         """, (user_id,))

#         conn.commit()
#         cursor.close()

#     except Exception as e:
#         print("❌ update_activity error:", e)

#     finally:
#         if conn:
#             conn.close()


# # ✅ Толық статистика (онлайнмен бірге)
# def get_full_stats():
#     conn = None
#     try:
#         conn = get_connection()
#         cursor = conn.cursor()

#         # Жалпы қолданушылар
#         cursor.execute("SELECT COUNT(*) FROM users;")
#         total_users = cursor.fetchone()[0]

#         # 24 сағат активті
#         cursor.execute("""
#             SELECT COUNT(*) FROM users
#             WHERE last_activity >= NOW() - INTERVAL '1 day';
#         """)
#         active_24h = cursor.fetchone()[0]

#         # Қазір онлайн (соңғы 5 минут)
#         cursor.execute("""
#             SELECT COUNT(*) FROM users
#             WHERE last_activity >= NOW() - INTERVAL '5 minutes';
#         """)
#         online_now = cursor.fetchone()[0]

#         # Барлық хабарламалар
#         cursor.execute("""
#             SELECT COALESCE(SUM(messages_count), 0) FROM users;
#         """)
#         total_messages = cursor.fetchone()[0]

#         cursor.close()

#         return total_users, active_24h, online_now, total_messages

#     except Exception as e:
#         print("❌ get_full_stats error:", e)
#         return 0, 0, 0, 0

#     finally:
#         if conn:
#             conn.close()


import os
import psycopg2
from psycopg2 import OperationalError
from dotenv import load_dotenv
import sys


# .env файлын жүктеу
load_dotenv(encoding='utf-8')

def get_connection():
    try:
        # Дерекқор параметрлерін алу
        dbname = os.getenv("DB_NAME")
        user = os.getenv("DB_USER") 
        password = os.getenv("DB_PASSWORD")
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "5432")
        
        # Егер .env мәндері жоқ болса, қолмен енгізуді сұрау
        if not dbname or not user or not password:
            print("❌ Дерекқор параметрлері .env файлында толық көрсетілмеген!")
            print("Қолмен енгізіңіз:")
            dbname = input("DB_NAME: ").strip()
            user = input("DB_USER: ").strip()
            password = input("DB_PASSWORD: ").strip()
            host = input("DB_HOST [localhost]: ").strip() or "localhost"
            port = input("DB_PORT [5432]: ").strip() or "5432"
        
        print(f"Қосылу әрекеті: {dbname}@{host}:{port}")
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port,
            client_encoding='UTF8',
            connect_timeout=10
        )
        print("✅ Дерекқорға сәтті қосылды!")
        
        # Таблицаны автоматты түрде құру (егер жоқ болса)
        create_users_table(conn)
        
        return conn
        
    except OperationalError as e:
        print("❌ Database connection error:", e)
        sys.exit(1)
    except Exception as e:
        print("❌ Unexpected error:", e)
        sys.exit(1)

def create_users_table(conn):
    """Егер жоқ болса, users таблицасын құру"""
    try:
        cursor = conn.cursor()
        
        # Таблицаның бар-жоғын тексеру
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                username VARCHAR(255),
                first_name VARCHAR(255),
                joined_at TIMESTAMP DEFAULT NOW(),
                last_activity TIMESTAMP DEFAULT NOW(),
                messages_count INTEGER DEFAULT 0
            );
        """)
        
        conn.commit()
        cursor.close()
        print("✅ 'users' таблицасы тексерілді/құрылды")
        
    except Exception as e:
        print(f"❌ Таблица құру кезінде қате: {e}")
        conn.rollback()

def _safe_text(value):
    if value is None:
        return ""
    
    if isinstance(value, bytes):
        try:
            return value.decode('utf-8', errors='replace').replace('\ufffd', '')
        except:
            return value.decode('latin-1', errors='replace')
    
    text = str(value)
    text = text.encode('utf-8', errors='replace').decode('utf-8', errors='replace')
    text = text.replace('\ufffd', '')
    text = text.replace('\xa0', ' ')
    text = ' '.join(text.split())
    
    return text

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
        print(f"✅ Қолданушы қосылды: {user_id} - {safe_username}")
        
    except Exception as e:
        print(f"❌ add_user error: {e}")
        if conn:
            conn.rollback()
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
        print(f"✅ Активтілік жаңартылды: {user_id}")

    except Exception as e:
        print("❌ update_activity error:", e)
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

# ✅ Толық статистика
def get_full_stats():
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM users;")
        total_users = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM users
            WHERE last_activity >= NOW() - INTERVAL '1 day';
        """)
        active_24h = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM users
            WHERE last_activity >= NOW() - INTERVAL '5 minutes';
        """)
        online_now = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COALESCE(SUM(messages_count), 0) FROM users;
        """)
        total_messages = cursor.fetchone()[0]

        cursor.close()
        print(f"📊 Статистика: {total_users} пайдаланушы, {active_24h} белсенді, {online_now} онлайн")
        
        return total_users, active_24h, online_now, total_messages

    except Exception as e:
        print("❌ get_full_stats error:", e)
        return 0, 0, 0, 0
    finally:
        if conn:
            conn.close()

# Таблицаны қолмен құру функциясы (бөлек шақыру үшін)
def init_database():
    """Дерекқорды инициализациялау - тек бір рет шақыру керек"""
    conn = None
    try:
        conn = get_connection()
        create_users_table(conn)
        print("✅ Дерекқор сәтті инициализацияланды!")
        return True
    except Exception as e:
        print(f"❌ Дерекқор инициализациясы қатесі: {e}")
        return False
    finally:
        if conn:
            conn.close()

# Егер бұл файлды тікелей іске қоссаңыз, дерекқорды инициализациялау
if __name__ == "__main__":
    print("🔄 Дерекқор инициализациялануда...")
    init_database()