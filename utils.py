# utils.py
import time
from collections import defaultdict, deque
from cryptography.fernet import Fernet, InvalidToken
from config import FERNET_KEY, VIEW_RATE_LIMIT, VIEW_RATE_WINDOW

_fernet = Fernet(FERNET_KEY.encode())

def encrypt(plain: str) -> bytes:
    return _fernet.encrypt(plain.encode())

def decrypt(blob: bytes) -> str | None:
    try:
        return _fernet.decrypt(blob).decode()
    except InvalidToken:
        return None

_buckets: dict[int, deque] = defaultdict(deque)

def rate_ok(key: int) -> bool:
    now = time.time()
    q = _buckets[key]
    while q and now - q[0] > VIEW_RATE_WINDOW:
        q.popleft()
    if len(q) >= VIEW_RATE_LIMIT:
        return False
    q.append(now)
    return True