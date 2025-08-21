
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.models.book import Book as BookModel
from app.schemas.book import Book, BookCreate
from app.database import get_db
from app.utils.logger import logger
from fastapi_pagination import Page, add_pagination, paginate
from typing import Optional
import os
from app.config import settings
import uuid

router = APIRouter(prefix="/books", tags=["books"])

@router.post("/", response_model=Book)
async def create_book(
    title: str = Form(...),
    author: str = Form(...),
    genre: str = Form(...),
    page_count: int = Form(...),
    publication_year: int = Form(...),
    description: Optional[str] = Form(None),
    cover_image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    try:
        cover_image_path = None
        if cover_image:
            # Ensure uploads directory exists
            os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
            # Generate unique filename
            file_extension = cover_image.filename.split(".")[-1]
            file_name = f"{uuid.uuid4()}.{file_extension}"
            file_path = os.path.join(settings.UPLOAD_DIR, file_name)
            # Save file
            with open(file_path, "wb") as f:
                content = await cover_image.read()
                f.write(content)
            cover_image_path = file_path

        db_book = BookModel(
            title=title,
            author=author,
            genre=genre,
            page_count=page_count,
            publication_year=publication_year,
            description=description,
            cover_image=cover_image_path
        )
        db.add(db_book)
        db.commit()
        db.refresh(db_book)
        logger.info(f"Created book: {db_book.title} by {db_book.author}")
        return db_book
    except Exception as e:
        logger.error(f"Error creating book: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/", response_model=Page[Book])
async def get_books(db: Session = Depends(get_db)):
    try:
        books = db.query(BookModel).all()
        logger.info("Fetched all books")
        return paginate(books)
    except Exception as e:
        logger.error(f"Error fetching books: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{id}", response_model=Book)
async def get_book(id: int, db: Session = Depends(get_db)):
    book = db.query(BookModel).filter(BookModel.id == id).first()
    if not book:
        logger.warning(f"Book with id {id} not found")
        raise HTTPException(status_code=404, detail="Book not found")
    logger.info(f"Fetched book: {book.title}")
    return book

@router.put("/{id}", response_model=Book)
async def update_book(
    id: int,
    title: str = Form(...),
    author: str = Form(...),
    genre: str = Form(...),
    page_count: int = Form(...),
    publication_year: int = Form(...),
    description: Optional[str] = Form(None),
    cover_image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    try:
        book = db.query(BookModel).filter(BookModel.id == id).first()
        if not book:
            logger.warning(f"Book with id {id} not found")
            raise HTTPException(status_code=404, detail="Book not found")

        book.title = title
        book.author = author
        book.genre = genre
        book.page_count = page_count
        book.publication_year = publication_year
        book.description = description

        if cover_image:
            # Ensure uploads directory exists
            os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
            # Generate unique filename
            file_extension = cover_image.filename.split(".")[-1]
            file_name = f"{uuid.uuid4()}.{file_extension}"
            file_path = os.path.join(settings.UPLOAD_DIR, file_name)
            # Save file
            with open(file_path, "wb") as f:
                content = await cover_image.read()
                f.write(content)
            book.cover_image = file_path

        db.commit()
        db.refresh(book)
        logger.info(f"Updated book: {book.title}")
        return book
    except Exception as e:
        logger.error(f"Error updating book: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{id}")
async def delete_book(id: int, db: Session = Depends(get_db)):
    try:
        book = db.query(BookModel).filter(BookModel.id == id).first()
        if not book:
            logger.warning(f"Book with id {id} not found")
            raise HTTPException(status_code=404, detail="Book not found")
        db.delete(book)
        db.commit()
        logger.info(f"Deleted book: {book.title}")
        return {"detail": "Book deleted"}
    except Exception as e:
        logger.error(f"Error deleting book: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/author/{author}", response_model=Page[Book])
async def get_books_by_author(author: str, db: Session = Depends(get_db)):
    try:
        books = db.query(BookModel).filter(BookModel.author.ilike(f"%{author}%")).all()
        logger.info(f"Fetched books by author: {author}")
        return paginate(books)
    except Exception as e:
        logger.error(f"Error fetching books by author: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/search/", response_model=Page[Book])
async def search_books(q: str, db: Session = Depends(get_db)):
    try:
        books = db.query(BookModel).filter(
            (BookModel.title.ilike(f"%{q}%")) | (BookModel.author.ilike(f"%{q}%"))
        ).all()
        logger.info(f"Search query: {q}")
        return paginate(books)
    except Exception as e:
        logger.error(f"Error searching books: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/filter/", response_model=Page[Book])
async def filter_books(
    genre: Optional[str] = None,
    publication_year: Optional[int] = None,
    db: Session = Depends(get_db)
):
    try:
        query = db.query(BookModel)
        if genre:
            query = query.filter(BookModel.genre.ilike(f"%{genre}%"))
        if publication_year:
            query = query.filter(BookModel.publication_year == publication_year)
        books = query.all()
        logger.info(f"Filtered books by genre: {genre}, year: {publication_year}")
        return paginate(books)
    except Exception as e:
        logger.error(f"Error filtering books: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

add_pagination(router)