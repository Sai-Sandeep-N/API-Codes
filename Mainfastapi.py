from fastapi import FastAPI,HTTPException
import fastapiSchemas
import fastapiDB
import inspect , time

app = FastAPI()

first_request = True

@app.get("/book/{ID}")
async def book_data(ID: int):
	try:
		result = await fastapiDB.getbook(ID)
		print(inspect.iscoroutinefunction(fastapiDB.getbook))
		return result
	except Exception as e:
		raise HTTPException(status_code=404,detail=repr(e))

@app.post("/book/")
async def create_book(request: fastapiSchemas.BookAuthorPayload):
	global first_request
	if first_request:
        # Sleep for 10 seconds on the first request
		time.sleep(10)
		first_request = False
	
	res= await fastapiDB.add_book(convert_into_book_db_model(request.book), convert_into_author_db_model(request.author))
	print(inspect.iscoroutinefunction(fastapiDB.add_book))
	if "already present" in res.lower():
		return "Book already present."
	else:
		print("Book named " + request.book.title + " added with total no. of pages = "
            + str(request.book.number_of_pages) + " author of book is "
            + request.author.first_name + " " + request.author.last_name)
		return ("Book named " + request.book.title + " added with total no. of pages = "
            + str(request.book.number_of_pages) + " author of book is "
            + request.author.first_name + " " + request.author.last_name)
	
	
@app.delete("/book/del/{ID}")
async def del_book(ID:int):
	print(inspect.iscoroutinefunction(fastapiDB.delbook))
	try:
		return await fastapiDB.delbook(ID)
	except Exception as e:
		raise HTTPException(status_code=404, detail=repr(e))


def convert_into_book_db_model(book: fastapiSchemas.Book):
	return fastapiDB.Book(title=book.title, number_of_pages=book.number_of_pages)

def convert_into_author_db_model(author: fastapiSchemas.Author):
	return fastapiDB.Author(first_name=author.first_name, last_name=author.last_name)
