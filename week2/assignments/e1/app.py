import sqlite3
from flask import Flask, jsonify, request, make_response

app = Flask(__name__)

DB = 'dumpdb.db'

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            status TEXT DEFAULT 'pending'
        )
    ''')

    conn.commit()
    conn.close()

init_db()


@app.get('/orders')
def list_orders():
    conn = get_db()
    rows = conn.execute('SELECT * FROM orders').fetchall()
    conn.close()

    orders = [dict(row) for row in rows]

    return jsonify({
        'data': orders,
        'total': len(orders)
    }), 200


@app.post('/orders')
def create_orders():
    if not request.is_json:
        return jsonify(error='expected JSON'), 415

    data = request.get_json(silent=True) or {}
    product = (data.get('product') or '').strip()
    quantity = data.get('quantity')

    if not product or not quantity:
        return jsonify(error='product and quantity required'), 422

    conn = get_db()
    cursor = conn.execute('INSERT INTO orders (product, quantity) VALUES (?, ?)', (product, quantity))
    order_id = cursor.lastrowid
    conn.commit()
    conn.close()

    order = {
        'id': order_id,
        'product': product,
        'quantity': quantity
    }

    resp = make_response(jsonify(order), 201)
    resp.headers['Location'] = f'/orders/{order_id}'

    return resp


@app.get('/orders/<int:oid>')
def get_order(oid):
    conn = get_db()
    order = conn.execute('SELECT * FROM orders WHERE id = ?', (oid,)).fetchone()
    conn.close()

    if order is None:
        return jsonify(error='not found'), 404

    return jsonify(dict(order)), 200

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)