import inspect
from sqlalchemy.orm import relationship, DeclarativeBase
from sqlalchemy import Column, String, Integer, ForeignKey, select, delete
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker


engine = create_async_engine('mysql+aiomysql://root:Mac.21/09@localhost:3306/books',echo=True)

SessionLocal = async_sessionmaker(engine)

class Base(DeclarativeBase):
    pass

class Author(Base):
       __tablename__ = 'authors'
       author_id = Column(Integer, primary_key=True)
       first_name = Column(String(length=50))
       last_name = Column(String(length=50))

class Book(Base):
       __tablename__ = 'books'
       
       book_id = Column(Integer, primary_key=True)
       title = Column(String(length=255))
       number_of_pages = Column(Integer)
       

class BookAuthor(Base):
       __tablename__ = 'bookauthors'

       bookauthor_id = Column(Integer, primary_key=True)
       author_id = Column(Integer, ForeignKey('authors.author_id'))
       book_id = Column(Integer, ForeignKey('books.book_id'))

       author = relationship("Author")
       book = relationship("Book")
 
async def getdb():
    async with engine.begin() as con:
        await con.run_sync(Base.metadata.create_all)
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()


async def add_book(book:Book, author:Author):
    async with AsyncSession(engine) as session:
        existing_book =await session.execute(select(Book).filter(Book.title==book.title, Book.number_of_pages==book.number_of_pages))
        existing_book = existing_book.scalar_one_or_none()
        if existing_book is not None:
            return "Book already present."
        print("Book does not exist. Adding book")
        session.add(book)
        existing_author =await session.execute(select(Author).filter(Author.first_name==author.first_name, Author.last_name==author.last_name))
        existing_author = existing_author.scalar_one_or_none()

        if existing_author is not None:
            print("Author has already been added")
            await session.flush()
            pairing =BookAuthor(author_id=existing_author.author_id, book_id=book.book_id)
        else:
            print("Author does not exist! Adding author")
            session.add(author)
            await session.flush()
            pairing =BookAuthor(author_id=author.author_id, book_id=book.book_id)

        session.add(pairing)
        await session.commit()
        await session.refresh(pairing)
        return "New pairing added " + str(pairing)


async def getbook(ID: int):
    async with AsyncSession(engine) as session:
        book =await session.execute(select(Book).filter(Book.book_id==ID))
        book = book.scalar_one_or_none()
        if book:
               pairing =await session.execute(select(BookAuthor).filter(BookAuthor.book_id==ID))
               pairing = pairing.scalar_one_or_none()
               author =await session.execute(select(Author).filter(Author.author_id==pairing.author_id))
               author = author.scalar_one_or_none()
               return (author,book)
        raise Exception("NO book with given ID")
     
async def delbook(ID:int):
    async with AsyncSession(engine) as session:
         book=await session.execute(select(Book).filter(Book.book_id==ID))
         book = book.scalar_one_or_none()
         if not book:
              raise Exception("Passed book id does not exist to delete")
         pairing =await session.execute(select(BookAuthor).filter(BookAuthor.book_id==ID))
         pairing = pairing.scalar_one_or_none()
         await session.execute(delete(BookAuthor).where(BookAuthor.book_id == ID))
         await session.execute(delete(Book).where(Book.book_id == ID))
         await session.execute(delete(Author).where(Author.author_id == ID))
         await session.commit()
         return f"Book with ID {ID} and its author have been deleted successfully."

