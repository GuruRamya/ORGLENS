"""
Token encryption — wraps Fernet symmetric encryption.
All OAuth tokens (Slack, Gmail) are encrypted at rest.

Usage:
    from app.services.security.token_encryption import encrypt_token, decrypt_token

    encrypted = encrypt_token("xoxb-slack-token-...")
    org.slack_access_token = encrypted          # store this

    raw = decrypt_token(org.slack_access_token) # use this
"""
import os
import base64
from typing import Optional
from cryptography.fernet import Fernet, InvalidToken
from loguru import logger


def _get_fernet() -> Fernet:
    """Load or generate encryption key from environment."""
    key = os.getenv("TOKEN_ENCRYPTION_KEY")
    if not key:
        raise RuntimeError(
            "TOKEN_ENCRYPTION_KEY is not set. "
            "Generate one with: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
        )
    try:
        return Fernet(key.encode() if isinstance(key, str) else key)
    except Exception:
        raise RuntimeError("TOKEN_ENCRYPTION_KEY is invalid. It must be a 32-byte URL-safe base64 string.")


def encrypt_token(plaintext: str) -> Optional[str]:
    """Encrypt a token string. Returns base64-encoded ciphertext or None."""
    if not plaintext:
        return None
    try:
        f = _get_fernet()
        return f.encrypt(plaintext.encode()).decode()
    except Exception as e:
        logger.error(f"Token encryption failed: {e}")
        return None


def decrypt_token(ciphertext: Optional[str]) -> Optional[str]:
    """Decrypt a stored token. Returns plaintext or None on failure."""
    if not ciphertext:
        return None
    try:
        f = _get_fernet()
        return f.decrypt(ciphertext.encode()).decode()
    except InvalidToken:
        logger.warning("Token decryption failed — token may be corrupted or key rotated")
        return None
    except Exception as e:
        logger.error(f"Token decryption error: {e}")
        return None


def generate_key() -> str:
    """Generate a new Fernet key. Run once and store in .env."""
    return Fernet.generate_key().decode()
