from models import Author, Book

def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"<title>" in response.data

def test_add_book(client, app):
    with app.app_context():
        author = Author(name='Author A')
        from models import db
        db.session.add(author)
        db.session.commit()

        response = client.post('/add_book', data={
            'title': 'Test Book',
            'genre': 'Test Genre',
            'author_id': author.id
        }, follow_redirects=True)
        assert response.status_code == 200

def test_create_author_and_book(app):
    with app.app_context():
        author = Author(name='Author A')
        book = Book(title='Book A', genre='Fiction', author=author)
        from models import db
        db.session.add(author)
        db.session.add(book)
        db.session.commit()

        assert Author.query.count() == 1
        assert Book.query.count() == 1
