from flask import Flask, request, jsonify
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from pydantic import BaseModel
import inspect #inspect.iscoroutinefunction(get_book_and_author) to check whether it was sync/async function
import time

DATABASE_URL = 'mysql+mysqlconnector://root:Mac.21/09@localhost:3306/flbooks'
engine = create_engine(DATABASE_URL)
Base = declarative_base()

SessionLocal = sessionmaker(bind=engine)

first_request = True

class BookBase(BaseModel):
    title: str
    pages: int

class AuthorBase(BaseModel):
    firstname: str
    lastname: str

class BookAuthorBase(BaseModel):
    book_id: int
    author_id: int


app = Flask(__name__)


class Author(Base):
    __tablename__ = "authors"
    authorid = Column(Integer, primary_key=True) 
    firstname = Column(String(length=50))
    lastname = Column(String(length=50))

class Book(Base):
    __tablename__ = "books"
    bookid = Column(Integer, primary_key=True) 
    title = Column(String(length = 255))
    pages = Column(Integer)

class BookAuthor(Base):
    __tablename__ = "bookauthors"
    bookauthorid = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey("books.bookid"))
    author_id = Column(Integer, ForeignKey("authors.authorid"))

    book = relationship("Author")
    author = relationship("Book")


Base.metadata.create_all(bind=engine)


def create_book_author_pairing(db, book: BookBase, author: AuthorBase):
    global first_request
    existing_book = db.query(Book).filter(Book.title == book.title).first()

    if existing_book:
        return jsonify({"message": "Book already exists"})

    new_book = Book(**book.dict())
    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    existing_author = db.query(Author).filter(Author.firstname == author.firstname,Author.lastname == author.lastname).first()

    if existing_author:
        author_id = existing_author.authorid
    else:
        new_author = Author(**author.dict())
        db.add(new_author)
        db.commit()
        db.refresh(new_author)
        author_id = new_author.authorid

    book_author_data = {"book_id": new_book.bookid, "author_id": author_id}
    new_book_author = BookAuthor(**book_author_data)
    db.add(new_book_author)
    db.commit()
    db.refresh(new_book_author)

    return jsonify({"message": "Book and Author added successfully"})


def get_book_and_author(db, book_id: int):
    book = db.query(Book).filter(Book.bookid == book_id).first()

    if book:
        pairing = db.query(BookAuthor).filter(BookAuthor.book_id == book_id).first()
        author = db.query(Author).filter(Author.authorid == pairing.author_id).first()
        return book, author
    raise Exception("No book found with the given ID")


def delete_book_and_author(db, book_id: int):
    book = db.query(Book).filter(Book.bookid == book_id).first()
    if not book:
        raise Exception(f"Book with ID {book_id} does not exist to delete")
    pairing = db.query(BookAuthor).filter(BookAuthor.book_id == book_id).first()
    if pairing:
        db.query(BookAuthor).filter(BookAuthor.book_id == book_id).delete()
        db.commit()
    db.query(Book).filter(Book.bookid == book_id).delete()
    db.query(Author).filter(Author.authorid == pairing.author_id).delete()
    db.commit()

    return f"Book with ID {book_id} and its author have been deleted successfully."


@app.route('/books/', methods=['POST'])
def create_book_author_pairing_route():
    global first_request
    request_data = request.json
    book_payload = request_data.get("book")
    author_payload = request_data.get("author")

    db = SessionLocal()
    if first_request:
        # Sleep for 10 seconds on the first request
        time.sleep(10)
        first_request = False
    result = create_book_author_pairing(db, BookBase(**book_payload), AuthorBase(**author_payload))
    db.close()
    print(result)
    print(inspect.iscoroutinefunction(create_book_author_pairing))
    return result


@app.route('/books/<int:book_id>', methods=['GET'])
def get_book_details(book_id: int):
    db = SessionLocal()
    try:
        book,author = get_book_and_author(db, book_id)
        result = {"book": {"title": book.title, "pages": book.pages}, "author": {"firstname": author.firstname, "lastname": author.lastname}}
        print(inspect.iscoroutinefunction(get_book_and_author))
        return jsonify(result)
    except Exception as e:
        print(inspect.iscoroutinefunction(get_book_and_author))
        return jsonify({"message": str(e)})


@app.route('/del/book/<int:id>', methods=['DELETE'])
def delete_book_details(id: int):
    db = SessionLocal()
    try:
        result_message = delete_book_and_author(db, id)
        return jsonify({"message": result_message})
    except Exception as e:
        return jsonify({"error": str(e)}), 404

if __name__ == "__main__":
    app.run(debug=True)
