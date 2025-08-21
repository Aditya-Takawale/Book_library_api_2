
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.models.book import Book as BookModel
from app.schemas.book import Book, BookCreate
from app.database import get_db
from fastapi_pagination import Page, add_pagination, paginate
from typing import Optional
import os
import logging
import uuid
import traceback

logger = logging.getLogger("BookLibraryAPI")

router = APIRouter(prefix="/books", tags=["books"])

@router.post("/", response_model=Book)
async def create_book(
    id: Optional[int] = Form(None),
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
        logger.debug(f"Received POST /books/ with title={title}, author={author}, genre={genre}, "
                     f"page_count={page_count}, publication_year={publication_year}, "
                     f"description={description}, cover_image={cover_image.filename if cover_image else None}")
        
        from app.config import settings
        cover_image_path = None
        if cover_image:
            # Ensure uploads directory exists
            os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
            # Generate unique filename
            file_extension = cover_image.filename.split(".")[-1].lower()
            if file_extension not in ["jpg", "jpeg", "png"]:
                logger.warning(f"Invalid file extension for cover_image: {file_extension}")
                raise HTTPException(status_code=400, detail="Only .jpg, .jpeg, or .png files are allowed")
            file_name = f"{uuid.uuid4()}.{file_extension}"
            file_path = os.path.join(settings.UPLOAD_DIR, file_name)
            # Save file
            try:
                with open(file_path, "wb") as f:
                    content = await cover_image.read()
                    f.write(content)
                cover_image_path = file_path
                logger.info(f"Saved cover image to {file_path}")
            except Exception as e:
                logger.error(f"Failed to save cover image: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Failed to save cover image: {str(e)}")

        # Optional explicit ID support for POST
        if id is not None:
            existing = db.query(BookModel).filter(BookModel.id == id).first()
            if existing:
                raise HTTPException(status_code=409, detail="Book with this id already exists")

        book_data = dict(
            title=title,
            author=author,
            genre=genre,
            page_count=page_count,
            publication_year=publication_year,
            description=description,
            cover_image=cover_image_path,
        )
        if id is not None:
            book_data["id"] = id

        db_book = BookModel(**book_data)
        db.add(db_book)
        db.commit()
        db.refresh(db_book)
        logger.info(f"Created book: {db_book.title} by {db_book.author} with ID {db_book.id}")
        return db_book
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error creating book: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/", response_model=Page[Book])
async def get_books(db: Session = Depends(get_db)):
    try:
        books = db.query(BookModel).all()
        logger.info("Fetched all books")
        return paginate(books)
    except Exception as e:
        logger.error(f"Error fetching books: {str(e)}\n{traceback.format_exc()}")
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

        from app.config import settings
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
            file_extension = cover_image.filename.split(".")[-1].lower()
            if file_extension not in ["jpg", "jpeg", "png"]:
                logger.warning(f"Invalid file extension for cover_image: {file_extension}")
                raise HTTPException(status_code=400, detail="Only .jpg, .jpeg, or .png files are allowed")
            file_name = f"{uuid.uuid4()}.{file_extension}"
            file_path = os.path.join(settings.UPLOAD_DIR, file_name)
            # Save file
            try:
                with open(file_path, "wb") as f:
                    content = await cover_image.read()
                    f.write(content)
                book.cover_image = file_path
                logger.info(f"Updated cover image to {file_path}")
            except Exception as e:
                logger.error(f"Failed to update cover image: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Failed to update cover image: {str(e)}")

        db.commit()
        db.refresh(book)
        logger.info(f"Updated book: {book.title}")
        return book
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error updating book: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

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
        logger.error(f"Error deleting book: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/author/{author}", response_model=Page[Book])
async def get_books_by_author(author: str, db: Session = Depends(get_db)):
    try:
        # MySQL doesn't support ILIKE; use LIKE with lower-casing for case-insensitivity
        from sqlalchemy import func
        books = (
            db.query(BookModel)
            .filter(func.lower(BookModel.author).like(f"%{author.lower()}%"))
            .all()
        )
        logger.info(f"Fetched books by author: {author}")
        return paginate(books)
    except Exception as e:
        logger.error(f"Error fetching books by author: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/search/", response_model=Page[Book])
async def search_books(q: str, db: Session = Depends(get_db)):
    try:
        from sqlalchemy import func
        q_lower = q.lower()
        books = (
            db.query(BookModel)
            .filter(
                (func.lower(BookModel.title).like(f"%{q_lower}%")) |
                (func.lower(BookModel.author).like(f"%{q_lower}%"))
            )
            .all()
        )
        logger.info(f"Search query: {q}")
        return paginate(books)
    except Exception as e:
        logger.error(f"Error searching books: {str(e)}\n{traceback.format_exc()}")
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
            from sqlalchemy import func
            query = query.filter(func.lower(BookModel.genre).like(f"%{genre.lower()}%"))
        if publication_year:
            query = query.filter(BookModel.publication_year == publication_year)
        books = query.all()
        logger.info(f"Filtered books by genre: {genre}, year: {publication_year}")
        return paginate(books)
    except Exception as e:
        logger.error(f"Error filtering books: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Internal server error")

add_pagination(router)