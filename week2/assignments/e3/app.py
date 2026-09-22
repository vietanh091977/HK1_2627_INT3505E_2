import hashlib
from flask import Flask, jsonify, request, make_response

app = Flask(__name__)

BOOKS = [
    {
        'id': 1, 'title': 'Clean Code', 'author': 'R. Martin', 'price': 29.99
    }
]

@app.get('/books/<int:bid>')
def get_book(bid):
    book = next((b for b in BOOKS if b['id'] == bid), None)

    if book is None:
        return jsonify(error='not fount'), 404

    book_string = str(book).encode('utf-8')
    etag = hashlib.md5(book_string).hexdigest()
    etag = f'"{etag}"'
    client_etag = request.headers.get('If-None-Match')

    if client_etag == etag:
        return '', 304

    resp = make_response(jsonify(book), 200)
    resp.headers['ETag'] = etag
    resp.headers['Cache-Control'] = 'public, max-age=60'

    return resp

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)