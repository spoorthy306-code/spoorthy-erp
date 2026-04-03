# SPOORTHY QUANTUM OS — Security
# PQC signatures, API keys, encryption

import base64
import os
import secrets
from datetime import datetime, timedelta
from typing import Optional

import jwt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from jwt.exceptions import PyJWTError as JWTError
from passlib.context import CryptContext

SECRET_KEY = os.getenv("SECRET_KEY", "")
if not SECRET_KEY:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY", "dev-only-insecure-default-change-in-prod"
    )
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_api_key() -> str:
    """Generate a secure API key"""
    return secrets.token_urlsafe(32)


def generate_pqc_keypair():
    """Generate PQC keypair (simulated - in real implementation use actual PQC)"""
    # For demo, using RSA as placeholder for PQC
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    return private_pem.decode(), public_pem.decode()


def sign_data_pqc(private_key_pem: str, data: bytes) -> str:
    """Sign data with PQC private key (simulated)"""
    private_key = serialization.load_pem_private_key(
        private_key_pem.encode(),
        password=None,
    )

    signature = private_key.sign(
        data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256(),
    )

    return base64.b64encode(signature).decode()


def verify_pqc_signature(
    data: bytes, signature: str, public_key_pem: Optional[str] = None
) -> bool:
    """Verify RSA signature (placeholder for PQC — swap in liboqs when available)"""
    if not public_key_pem:
        return False
    try:
        public_key = serialization.load_pem_public_key(public_key_pem.encode())
        raw_sig = base64.b64decode(signature)
        public_key.verify(
            raw_sig,
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
        return True
    except Exception:
        return False


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except (JWTError, Exception):
        return None


def _get_fernet() -> Fernet:
    raw_key = os.getenv("ENCRYPTION_KEY", "")
    if not raw_key:
        raise RuntimeError("ENCRYPTION_KEY environment variable must be set")
    return Fernet(raw_key.encode())


def encrypt_sensitive_data(data: str, key: Optional[str] = None) -> str:
    """Encrypt sensitive data with Fernet symmetric encryption"""
    f = _get_fernet()
    return f.encrypt(data.encode()).decode()


def decrypt_sensitive_data(encrypted_data: str, key: Optional[str] = None) -> str:
    """Decrypt sensitive data with Fernet symmetric encryption"""
    f = _get_fernet()
    return f.decrypt(encrypted_data.encode()).decode()


def generate_secure_token(length: int = 32) -> str:
    """Generate a secure random token"""
    return secrets.token_hex(length)
