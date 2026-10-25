"""Inventory repository: parameterized queries and atomic stock transitions."""
from fastapi import HTTPException
from backend.db import connect


def serialize(row):
    value = dict(row)
    value['price'] = value.pop('price_cents') / 100
    return value


def list_vehicles(path, make='', model='', category='', min_price=None, max_price=None):
    clauses, params = [], []
    for field, value in [('make',make),('model',model),('category',category)]:
        if value:
            # instr treats %, _ and quotes as literal characters, not SQL patterns.
            clauses.append(f'instr(lower({field}),lower(?)) > 0')
            params.append(value)
    for operator, value in [('>=',min_price),('<=',max_price)]:
        if value is not None:
            clauses.append(f'price_cents {operator} ?')
            params.append(float(value * 100))
    sql = 'SELECT * FROM vehicles' + (' WHERE '+' AND '.join(clauses) if clauses else '') + ' ORDER BY id DESC'
    with connect(path) as db:
        return [serialize(row) for row in db.execute(sql, params)]


def save(path, data, vehicle_id=None):
    values = (data.make, data.model, data.category, int(data.price * 100), data.quantity)
    with connect(path) as db:
        if vehicle_id is None:
            result = db.execute('INSERT INTO vehicles(make,model,category,price_cents,quantity) VALUES (?,?,?,?,?)',values)
            vehicle_id = result.lastrowid
        else:
            result = db.execute('UPDATE vehicles SET make=?,model=?,category=?,price_cents=?,quantity=? WHERE id=?', values+(vehicle_id,))
            if not result.rowcount:
                raise HTTPException(404,'Vehicle not found')
        return serialize(db.execute('SELECT * FROM vehicles WHERE id=?',(vehicle_id,)).fetchone())


def change_stock(path, vehicle_id, amount, restock=False):
    with connect(path) as db:
        # Check and mutation happen in a single write, so concurrent buyers cannot oversell.
        if restock:
            result = db.execute('UPDATE vehicles SET quantity=quantity+? WHERE id=? AND quantity+?<=1000000',(amount,vehicle_id,amount))
        else:
            result = db.execute('UPDATE vehicles SET quantity=quantity-? WHERE id=? AND quantity>=?',(amount,vehicle_id,amount))
        if not result.rowcount:
            exists = db.execute('SELECT id FROM vehicles WHERE id=?',(vehicle_id,)).fetchone()
            if not exists:
                raise HTTPException(404,'Vehicle not found')
            raise HTTPException(409,'Stock limit exceeded' if restock else 'Insufficient stock')
        return serialize(db.execute('SELECT * FROM vehicles WHERE id=?',(vehicle_id,)).fetchone())


def delete(path, vehicle_id):
    with connect(path) as db:
        if not db.execute('DELETE FROM vehicles WHERE id=?',(vehicle_id,)).rowcount:
            raise HTTPException(404,'Vehicle not found')
