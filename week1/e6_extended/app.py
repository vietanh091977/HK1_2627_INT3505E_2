from flask import Flask, jsonify, request

app = Flask(__name__)

_next = 3

BOOKS = [
    {
        'id': 1, 'title': 'Clean Code', 'author': 'R. Martin', 'year': 2008
    },
    {
        'id': 2, 'title': 'The Pragmatic Programmer', 'author': 'A. Hunt', 'year': 1999
    }
]

def find(bid):
    return next((b for b in BOOKS if b['id'] == bid), None)

def validate_year(year):
    return isinstance(year, int) and not isinstance(year, bool) and year >= 1900

# LIST - GET /books
@app.route('/books', methods=['GET'])
def list_books():
    # (a) Tìm kiếm GET /books?q=...
    q = request.args.get('q', '').strip().lower()

    # (b) Sort theo ?sort=title
    sort = request.args.get('sort')

    books = BOOKS

    if q:
        books = [b for b in books if q in b['title'].lower() or q in b['author'].lower()]

    if sort:
        if sort != 'title':
            return jsonify({'error': 'unsupported sort field'}), 400
        books = sorted(books, key=lambda b: b['title'].lower())

    n = int(request.args.get('limit', 100))
    return jsonify(books[:n]), 200

# DETAIL - GET /books/<int:id>
@app.route('/books/<int:bid>', methods=['GET'])
def get_book(bid):
    book = find(bid)
    if not book:
        return jsonify({'error': 'not found'}), 404
    return jsonify(book), 200

# CREATE - POST /books
@app.route('/books', methods=['POST'])
def create_book():
    global _next
    body = request.get_json(silent=True) or {}
    t, a, y = body.get('title'), body.get('author'), body.get('year')

    if not t or not a:
        return jsonify({'error': 'need title+author'}), 400

    # (c) Bắt buộc field year là số >= 1900
    if not validate_year(y):
        return jsonify({'error': 'invalid year'}), 400
    
    book = {'id': _next, 'title': t, 'author': a, 'year': y}
    _next += 1
    BOOKS.append(book)

    return jsonify(book), 201, {"Location": f"/books/{book['id']}"}

# UPDATE - PUT, DELETE - DELETE
@app.route('/books/<int:bid>', methods=['PUT', 'DELETE'])
def modify_book(bid):
    book = find(bid)

    if not book:
        return jsonify({'error': 'not found'}), 404
    
    if request.method == 'PUT':
        body = request.get_json(silent=True) or {}

        if 'year' in body and not validate_year(body['year']):
            return jsonify({'error': 'invalid year'}), 400

        book.update(body)
        return jsonify(book), 200
        
    BOOKS.remove(book)
    return '', 204

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)