"""Password hashing and short-lived, signed access tokens."""
from datetime import datetime, timedelta, timezone
import jwt
from pwdlib import PasswordHash

passwords = PasswordHash.recommended()
DUMMY_HASH = passwords.hash('dummy-password-for-timing-only')

def token_for(user_id, secret):
    now = datetime.now(timezone.utc)
    return jwt.encode({'sub': str(user_id), 'iat': now, 'exp': now + timedelta(hours=1)}, secret, algorithm='HS256')
