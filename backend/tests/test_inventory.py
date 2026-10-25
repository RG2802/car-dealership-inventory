from concurrent.futures import ThreadPoolExecutor
import pytest
from fastapi.testclient import TestClient
from backend.app import create_app
from .test_auth import SECRET

CAR = {'make':'Toyota','model':'Camry','category':'Sedan','price':'32500.25','quantity':2}

@pytest.fixture
def vehicle(client, user):
    r = client.post('/api/vehicles', json=CAR, headers=user)
    assert r.status_code == 201
    return r.json()

def test_crud_and_persistence(client, user, vehicle):
    assert vehicle['price'] == 32500.25
    assert client.get('/api/vehicles', headers=user).json() == [vehicle]
    updated = {**CAR, 'model':'Corolla'}
    assert client.put(f"/api/vehicles/{vehicle['id']}", json=updated, headers=user).json()['model'] == 'Corolla'
    with TestClient(create_app(client.app.state.db_path, SECRET)) as fresh:
        assert fresh.get('/api/vehicles', headers=user).json()[0]['model'] == 'Corolla'

@pytest.mark.parametrize('query,expected', [('make=toy',1),('model=CAM',1),('category=sedan',1),('min_price=32500&max_price=32501',1),('max_price=100',0),('make=Ford',0),('make=%25',0),('make=%27%20OR%201%3D1--',0)])
def test_search(client, user, vehicle, query, expected):
    r = client.get('/api/vehicles/search?'+query, headers=user)
    assert r.status_code == 200
    assert len(r.json()) == expected

@pytest.mark.parametrize('query', ['min_price=-1','min_price=100&max_price=1','max_price=NaN'])
def test_invalid_price_filter(client, user, query):
    assert client.get('/api/vehicles/search?'+query, headers=user).status_code == 422

@pytest.mark.parametrize('field,value', [('price',-1),('price','1.234'),('quantity',-1),('quantity',1.5),('quantity',True),('make','  '),('model',''),('category','')])
def test_invalid_vehicle(client, user, field, value):
    assert client.post('/api/vehicles', headers=user, json={**CAR,field:value}).status_code == 422

def test_purchase_and_out_of_stock(client, user, vehicle):
    url = f"/api/vehicles/{vehicle['id']}/purchase"
    assert client.post(url, headers=user, json={'quantity':2}).json()['quantity'] == 0
    assert client.post(url, headers=user, json={'quantity':1}).status_code == 409
    assert client.get('/api/vehicles', headers=user).json()[0]['quantity'] == 0

@pytest.mark.parametrize('qty', [0,-1,1.2,True,1000001])
def test_invalid_purchase(client, user, vehicle, qty):
    assert client.post(f"/api/vehicles/{vehicle['id']}/purchase", headers=user, json={'quantity':qty}).status_code == 422

def test_admin_permissions(client, user, vehicle):
    url = f"/api/vehicles/{vehicle['id']}"
    assert client.delete(url, headers=user).status_code == 403
    assert client.post(url+'/restock', headers=user, json={'quantity':1}).status_code == 403

def test_admin_restock_delete(client, admin, vehicle):
    url = f"/api/vehicles/{vehicle['id']}"
    assert client.post(url+'/restock', headers=admin, json={'quantity':3}).json()['quantity'] == 5
    assert client.delete(url, headers=admin).status_code == 204
    assert client.get('/api/vehicles', headers=admin).json() == []
    assert client.delete(url, headers=admin).status_code == 404

@pytest.mark.parametrize('method,path,body', [('post','',CAR),('put','/1',CAR),('delete','/1',None),('post','/1/purchase',{'quantity':1}),('post','/1/restock',{'quantity':1}),('get','/search',None)])
def test_all_routes_require_auth(client, method, path, body):
    assert client.request(method,'/api/vehicles'+path,json=body).status_code == 401

@pytest.mark.parametrize('method,path,body', [('put','',CAR),('post','/purchase',{'quantity':1}),('post','/restock',{'quantity':1})])
def test_missing_vehicle(client, admin, method, path, body):
    assert client.request(method,'/api/vehicles/999'+path,headers=admin,json=body).status_code == 404

def test_concurrent_purchase_cannot_oversell(client, user, vehicle):
    def buy(_):
        return client.post(f"/api/vehicles/{vehicle['id']}/purchase",headers=user,json={'quantity':1}).status_code
    with ThreadPoolExecutor(max_workers=8) as pool:
        statuses = list(pool.map(buy, range(8)))
    assert statuses.count(200) == 2
    assert statuses.count(409) == 6
    assert client.get('/api/vehicles',headers=user).json()[0]['quantity'] == 0

def test_restock_limit(client, admin, vehicle):
    assert client.post(f"/api/vehicles/{vehicle['id']}/restock", headers=admin,json={'quantity':1000000}).status_code == 409
