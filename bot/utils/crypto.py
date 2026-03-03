# ...\secure-crypto-bot\bot\utils\crypto.py

# import hashlib
# import base64
# from cryptography.fernet import Fernet

# def get_crypto_key(user_code: str) -> bytes:
#     # 5 таңбалы кодты 32-байттық кілтке айналдыру
#     hashed = hashlib.sha256(user_code.encode()).digest()
#     return base64.urlsafe_b64encode(hashed)

# def encrypt_text(text: str, key: bytes) -> str:
#     f = Fernet(key)
#     return f.encrypt(text.encode()).decode()

# def decrypt_text(text: str, key: bytes) -> str:
#     f = Fernet(key)
#     return f.decrypt(text.encode()).decode()

# # Жаңа: Файлдарды (суреттерді) шифрлау
# def encrypt_file(file_bytes: bytes, key: bytes) -> bytes:
#     f = Fernet(key)
#     return f.encrypt(file_bytes)

# # Жаңа: Файлдарды (суреттерді) дешифрлау
# def decrypt_file(file_bytes: bytes, key: bytes) -> bytes:
#     f = Fernet(key)
#     return f.decrypt(file_bytes)



import hashlib
import base64
import struct
from cryptography.fernet import Fernet, InvalidToken

# Тұрақты тұз (Salt) - бұл кілтті іріктеуді қиындатады
SALT = b'secure_storage_salt_v1' 

def get_crypto_key(user_code: str) -> bytes:
    """5-таңбалы кодты PBKDF2 арқылы 32-байттық күшті кілтке айналдыру"""
    kdf = hashlib.pbkdf2_hmac(
        'sha256', 
        user_code.encode(), 
        SALT, 
        100000  # 100,000 итерация - брутфорсқа қарсы тосқауыл
    )
    return base64.urlsafe_b64encode(kdf)

def encrypt_data(data: bytes, key: bytes) -> bytes:
    f = Fernet(key)
    return f.encrypt(data)

def decrypt_data(data: bytes, key: bytes) -> bytes:
    f = Fernet(key)
    return f.decrypt(data)

def pack_file(filename: str, file_data: bytes) -> bytes:
    """Файл атын және мәліметтерін бірге орау"""
    name_bytes = filename.encode('utf-8')
    name_len = len(name_bytes)
    # Формат: [Атының ұзындығы (4 байт)] + [Аты] + [Файл мәліметтері]
    return struct.pack("I", name_len) + name_bytes + file_data

def unpack_file(packed_data: bytes):
    """Орамды жазып, файл атын және мәліметтерін алу"""
    name_len = struct.unpack("I", packed_data[:4])[0]
    filename = packed_data[4:4+name_len].decode('utf-8')
    file_data = packed_data[4+name_len:]
    return filename, file_data