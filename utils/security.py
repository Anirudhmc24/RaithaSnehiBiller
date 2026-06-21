# utils/security.py
import hashlib
import os
import hmac

def hash_password(password: str, salt: str = None) -> tuple[str, str]:
    """
    Hash a password securely using PBKDF2 SHA256 with 100,000 iterations.
    Returns (hash_hex, salt).
    """
    if salt is None:
        salt = os.urandom(16).hex()
    
    hash_bytes = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    )
    return hash_bytes.hex(), salt

def verify_password(password: str, hash_hex: str, salt: str) -> bool:
    """
    Verify a password against a hash using constant-time comparison.
    """
    try:
        new_hash, _ = hash_password(password, salt)
        return hmac.compare_digest(new_hash.encode('utf-8'), hash_hex.encode('utf-8'))
    except Exception:
        return False
