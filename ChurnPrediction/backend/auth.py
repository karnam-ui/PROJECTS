#this is for generating and hashing passwrord and jwt tokens for user registration and login
from fastapi import HTTPException

from jose import JWTError, jwt #python-jose library for handling JWT tokens
from passlib.context import CryptContext #passlib library for hashing passwords
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from fastapi import Header
load_dotenv() # Load environment variables from .env file

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 #token will expire after 30 minutes

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 1. Hash a password
def hash_password(password: str):
    return pwd_context.hash(password)

# 2. Verify password against hash
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

# 3. Create JWT token
def create_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# 4. Verify and decode token
def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

#extract token from Authorization header
def get_token_from_header(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    token = authorization[len("Bearer "):]
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload
