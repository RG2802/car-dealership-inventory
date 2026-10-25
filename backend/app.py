import os
import sqlite3
import jwt
from fastapi import FastAPI, Depends, HTTPException, Query, Response
from decimal import Decimal
from backend import inventory
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from backend.db import connect, initialize
from backend.schemas import Credentials, VehicleInput, StockInput
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

    def admin_user(user=Depends(current_user)):
        if user['role'] != 'admin':
            raise HTTPException(403, 'Administrator access required')
        return user

    @app.get('/api/vehicles')
    def vehicles(user=Depends(current_user)):
        return inventory.list_vehicles(db_path)

    @app.get('/api/vehicles/search')
    def search(make: str = Query('', max_length=80), model: str = Query('', max_length=80),
               category: str = Query('', max_length=40),
               min_price: Decimal | None = Query(None, ge=0, le=100000000),
               max_price: Decimal | None = Query(None, ge=0, le=100000000), user=Depends(current_user)):
        if min_price is not None and max_price is not None and min_price > max_price:
            raise HTTPException(422, 'Minimum price must not exceed maximum price')
        return inventory.list_vehicles(db_path, make, model, category, min_price, max_price)

    @app.post('/api/vehicles', status_code=201)
    def add(data: VehicleInput, user=Depends(current_user)):
        return inventory.save(db_path, data)

    @app.put('/api/vehicles/{vehicle_id}')
    def update(vehicle_id: int, data: VehicleInput, user=Depends(current_user)):
        return inventory.save(db_path, data, vehicle_id)

    @app.delete('/api/vehicles/{vehicle_id}', status_code=204)
    def remove(vehicle_id: int, user=Depends(admin_user)):
        inventory.delete(db_path, vehicle_id)
        return Response(status_code=204)

    @app.post('/api/vehicles/{vehicle_id}/purchase')
    def purchase(vehicle_id: int, data: StockInput, user=Depends(current_user)):
        return inventory.change_stock(db_path, vehicle_id, data.quantity)

    @app.post('/api/vehicles/{vehicle_id}/restock')
    def restock(vehicle_id: int, data: StockInput, user=Depends(admin_user)):
        return inventory.change_stock(db_path, vehicle_id, data.quantity, restock=True)

    return app
