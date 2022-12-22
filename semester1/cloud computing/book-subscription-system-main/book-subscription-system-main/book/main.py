from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from model import Books
from database import SessionLocal, engine
import model

app = FastAPI()

model.Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*']
)


def get_database_session():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.get("/books")
async def read_orders(request: Request, db: Session = Depends(get_database_session)):
    orders = db.query(Books).all()
    return orders

@app.post("/books")
async def create_order(request: Request, db: Session = Depends(get_database_session)):
    data = await request.json()
    books = Books(book_name=data["book_name"], price=data["price"], quantity=data["quantity"])
    db.add(books)
    db.commit()
    db.refresh(books)
    response = RedirectResponse('/books', status_code=303)
    return response

@app.delete("/books/{id}")
async def delete_book(request: Request, id: int, db: Session = Depends(get_database_session)):
    book = db.query(Books).get(id)
    db.delete(book)
    db.commit()
    return JSONResponse(status_code=200, content={
        "status_code": 200,
        "message": "success",
        "book": None
    })

@app.patch("/books/{id}")
async def update_book(request: Request, id: int, db: Session = Depends(get_database_session)):
    requestBody = await request.json()
    book = db.query(Books).get(id)
    book.quantity = requestBody['update_num']
    db.commit()
    db.refresh(book)
    newBook = jsonable_encoder(book)
    return JSONResponse(status_code=200, content={
        "status_code": 200,
        "message": "success",
        "book": newBook
    })

@app.patch("/books/buy/{id}")
async def update_book(request: Request, id: int, db: Session = Depends(get_database_session)):
    requestBody = await request.json()
    book = db.query(Books).get(id)
    book.quantity = book.quantity - int(requestBody.split('"')[-2])
    db.commit()
    db.refresh(book)
    newBook = jsonable_encoder(book)
    return JSONResponse(status_code=200, content={
        "status_code": 200,
        "message": "success",
        "book": newBook
    })

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)