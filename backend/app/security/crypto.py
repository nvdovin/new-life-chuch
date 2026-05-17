import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.core.config import settings


def _key() -> bytes:
    key = base64.b64decode(settings.aes_key_b64)
    if len(key) != 32:
        raise ValueError('AES key must be 32 bytes')
    return key


def encrypt_text(value: str) -> bytes:
    nonce = os.urandom(12)
    aes = AESGCM(_key())
    data = value.encode('utf-8')
    ct = aes.encrypt(nonce, data, None)
    return nonce + ct


def decrypt_text(blob: bytes) -> str:
    nonce, ct = blob[:12], blob[12:]
    aes = AESGCM(_key())
    return aes.decrypt(nonce, ct, None).decode('utf-8')
