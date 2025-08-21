from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from app.models.book import Book
from app.schemas.book import BookCreate, BookResponse, BookUpdate
from app.database import get_db
from app.utils.logger import logger
from fastapi_pagination import Page, paginate, add_pagination
import os
from app.config import settings
import uuid

router = APIRouter(prefix="/books", tags=["books"])

@router.post("/", response_model=BookResponse)
async def create_book(book: BookCreate, file: Optional[UploadFile] = None, db: Session = Depends(get_db)):
    logger.info(f"Creating new book: {book.title}")
    try:
        db_book = Book(**book.dict(exclude_unset=True))
        
        if file:
            os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
            file_extension = file.filename.split('.')[-1]
            file_name = f"{uuid.uuid4()}.{file_extension}"
            file_path = os.path.join(settings.UPLOAD_DIR, file_name)
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            db_book.cover_image = file_path
            
        db.add(db_book)
        db.commit()
        db.refresh(db_book)
        logger.info(f"Book created successfully: {db_book.id}")
        return db_book
    except Exception as e:
        logger.error(f"Error creating book: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=Page[BookResponse])
async def get_books(db: Session = Depends(get_db)):
    logger.info("Fetching all books")
    try:
        books = db.query(Book).all()
        return paginate(books)
    except Exception as e:
        logger.error(f"Error fetching books: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{book_id}", response_model=BookResponse)
async def get_book(book_id: int, db: Session = Depends(get_db)):
    logger.info(f"Fetching book with id: {book_id}")
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        logger.warning(f"Book not found: {book_id}")
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@router.put("/{book_id}", response_model=BookResponse)
async def update_book(book_id: int, book: BookUpdate, file: Optional[UploadFile] = None, db: Session = Depends(get_db)):
    logger.info(f"Updating book with id: {book_id}")
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if not db_book:
        logger.warning(f"Book not found for update: {book_id}")
        raise HTTPException(status_code=404, detail="Book not found")
    
    try:
        update_data = book.dict(exclude_unset=True)
        if file:
            os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
            file_extension = file.filename.split('.')[-1]
            file_name = f"{uuid.uuid4()}.{file_extension}"
            file_path = os.path.join(settings.UPLOAD_DIR, file_name)
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            update_data["cover_image"] = file_path
            
        for key, value in update_data.items():
            setattr(db_book, key, value)
            
        db.commit()
        db.refresh(db_book)
        logger.info(f"Book updated successfully: {book_id}")
        return db_book
    except Exception as e:
        logger.error(f"Error updating book: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{book_id}")
async def delete_book(book_id: int, db: Session = Depends(get_db)):
    logger.info(f"Deleting book with id: {book_id}")
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        logger.warning(f"Book not found for deletion: {book_id}")
        raise HTTPException(status_code=404, detail="Book not found")
    
    try:
        if book.cover_image and os.path.exists(book.cover_image):
            os.remove(book.cover_image)
        db.delete(book)
        db.commit()
        logger.info(f"Book deleted successfully: {book_id}")
        return {"message": "Book deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting book: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/author/{author}", response_model=Page[BookResponse])
async def get_books_by_author(author: str, db: Session = Depends(get_db)):
    logger.info(f"Fetching books by author: {author}")
    try:
        books = db.query(Book).filter(Book.author.ilike(f"%{author}%")).all()
        return paginate(books)
    except Exception as e:
        logger.error(f"Error fetching books by author: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/search/", response_model=Page[BookResponse])
async def search_books(q: str, db: Session = Depends(get_db)):
    logger.info(f"Searching books with query: {q}")
    try:
        books = db.query(Book).filter(
            or_(Book.title.ilike(f"%{q}%"), Book.author.ilike(f"%{q}%"))
        ).all()
        return paginate(books)
    except Exception as e:
        logger.error(f"Error searching books: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/filter/", response_model=Page[BookResponse])
async def filter_books(
    genre: Optional[str] = Query(None),
    publication_year: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    logger.info(f"Filtering books with params: genre={genre}, year={publication_year}")
    try:
        query = db.query(Book)
        if genre:
            query = query.filter(Book.genre.ilike(f"%{genre}%"))
        if publication_year:
            query = query.filter(Book.publication_year == publication_year)
        books = query.all()
        return paginate(books)
    except Exception as e:
        logger.error(f"Error filtering books: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

add_pagination(router)