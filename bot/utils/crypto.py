import hashlib
import base64
from cryptography.fernet import Fernet

def get_crypto_key(user_code: str) -> bytes:
    hashed = hashlib.sha256(user_code.encode()).digest()
    return base64.urlsafe_b64encode(hashed)

def encrypt_text(text: str, key: bytes) -> str:
    f = Fernet(key)
    return f.encrypt(text.encode()).decode()

def decrypt_text(text: str, key: bytes) -> str:
    f = Fernet(key)
    return f.decrypt(text.encode()).decode()