# user/encryption.py
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64
import os
from decouple import config

# AES-256 key (must be exactly 32 bytes)
AES_KEY_B64 = config('AES_SECRET_KEY')


if not AES_KEY_B64:
    raise RuntimeError("AES_SECRET_KEY not set")

AES_KEY = base64.b64decode(AES_KEY_B64)

if len(AES_KEY) != 32:
    raise ValueError("AES_SECRET_KEY must be 32 bytes (AES-256)")
BLOCK_SIZE = 16  # AES block size

# Pad plaintext to a multiple of BLOCK_SIZE
def pad(data: bytes) -> bytes:
    padding_len = BLOCK_SIZE - len(data) % BLOCK_SIZE
    return data + bytes([padding_len]) * padding_len

# Remove padding after decryption
def unpad(data: bytes) -> bytes:
    return data[:-data[-1]]

# Encrypt a string with AES-256-CBC and random IV
def encrypt_aes256(plaintext: str) -> str:
    data = pad(plaintext.encode('utf-8'))
    iv = get_random_bytes(BLOCK_SIZE)
    cipher = AES.new(AES_KEY, AES.MODE_CBC, iv)
    ct_bytes = cipher.encrypt(data)
    # Store IV + ciphertext together, then encode as base64
    return base64.b64encode(iv + ct_bytes).decode('utf-8')

# Decrypt AES-256-CBC string
def decrypt_aes256(token: str) -> str:
    raw = base64.b64decode(token)
    iv = raw[:BLOCK_SIZE]
    ct = raw[BLOCK_SIZE:]
    cipher = AES.new(AES_KEY, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(ct)
    return unpad(decrypted).decode('utf-8')
