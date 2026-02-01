from fastapi import Body, FastAPI

app = FastAPI()



BOOKS = [
    {
        "id": 1,
        "title": "1984",
        "author": "George Orwell",
        "category": "Science"
    },
    {
        "id": 2,
        "title": "To Kill a Mockingbird",
        "author": "Harper Lee",
        "category": "History"
    },
    {
        "id": 3,
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "category": "Maths"
    },
]
     

@app.get("/books")
async def read_all_books():
    return BOOKS


@app.get("/books/{book_id}")
async def read_book(book_id: int):
    for book in BOOKS:
        if book["id"] == book_id:
            return book
    return {"error": "Book not found"}  

@app.get("/books/category/")
def read_category_books(category: str):
    category_books = [book for book in BOOKS if book["category"].lower() == category.lower()]
    return category_books

@app.post("/books/")
async def create_book(new_book= Body()):
    BOOKS.append(new_book)

@app.put("/books/update_book")
async def update_book(updated_book= Body()):
    for i in range(len(BOOKS)):
        if BOOKS[i]["id"] == updated_book["id"]:
            BOOKS[i] = updated_book
            return {"message": "Book updated successfully"}
        
@app.delete("/books/{book_id}")
async def delete_book(book_id: int):
    for i in range(len(BOOKS)):
        if BOOKS[i]["id"] == book_id:
            BOOKS.pop(i)
            return {"message": "Book deleted successfully"}