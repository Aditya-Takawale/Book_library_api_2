from pydantic import BaseModel

class BookBorrowRequest(BaseModel):
    book_id: int
