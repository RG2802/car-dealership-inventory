import os
import sqlite3
import jwt
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from backend.db import connect, initialize
from backend.schemas import Credentials
from backend.security import passwords, DUMMY_HASH, token_for

bearer = HTTPBearer(auto_error=False)

def create_app(db_path=None, secret=None):
    db_path = db_path or os.environ.get('DATABASE_PATH', 'data/dealership.db')
    secret = secret or os.environ.get('JWT_SECRET', '')
    if len(secret) < 32:
        raise RuntimeError('JWT_SECRET must contain at least 32 characters')
    initialize(db_path)
    app = FastAPI(title='Apex Motors Inventory', version='1.0.0')
    app.state.db_path = db_path
    app.add_middleware(CORSMiddleware, allow_origins=[os.environ.get('FRONTEND_ORIGIN', 'http://localhost:5173')], allow_methods=['GET','POST','PUT','DELETE'], allow_headers=['Authorization','Content-Type'])

    def current_user(auth: HTTPAuthorizationCredentials = Depends(bearer)):
        try:
            if not auth:
                raise ValueError()
            payload = jwt.decode(auth.credentials, secret, algorithms=['HS256'], options={'require': ['sub','exp','iat']})
            with connect(db_path) as db:
                user = db.execute('SELECT id,email,role FROM users WHERE id=?', (int(payload['sub']),)).fetchone()
            if not user:
                raise ValueError()
            return dict(user)
        except (jwt.PyJWTError, ValueError, TypeError):
            raise HTTPException(401, 'Invalid or expired access token', headers={'WWW-Authenticate': 'Bearer'})

    def session(user):
        return {'access_token': token_for(user['id'], secret), 'token_type': 'bearer', 'user': {k: user[k] for k in ('id','email','role')}}

    @app.post('/api/auth/register', status_code=201)
    def register(data: Credentials):
        hashed = passwords.hash(data.password)
        try:
            with connect(db_path) as db:
                result = db.execute('INSERT INTO users(email,password_hash) VALUES (?,?)', (str(data.email).lower(), hashed))
                user = {'id': result.lastrowid, 'email': str(data.email).lower(), 'role': 'user'}
            return session(user)
        except sqlite3.IntegrityError:
            raise HTTPException(409, 'Email is already registered')

    @app.post('/api/auth/login')
    def login(data: Credentials):
        with connect(db_path) as db:
            user = db.execute('SELECT * FROM users WHERE email=?', (str(data.email).lower(),)).fetchone()
        valid = passwords.verify(data.password, user['password_hash'] if user else DUMMY_HASH)
        if not user or not valid:
            raise HTTPException(401, 'Incorrect email or password')
        return session(user)

    @app.get('/api/auth/me')
    def me(user=Depends(current_user)):
        return user

    @app.get('/api/vehicles')
    def vehicles(user=Depends(current_user)):
        return []

    return app
