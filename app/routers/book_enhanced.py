from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.schemas.book import BookResponse, BookCreate, BookUpdate
from app.services.book_service import BookService
from app.utils.dependencies import get_admin_user, get_current_user
from app.database import get_db
from typing import Optional, List
import logging

logger = logging.getLogger("BookLibraryAPI")

router = APIRouter(prefix="/books", tags=["Books"])

@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(
    book_data: BookCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)  # Only admins can create books
):
    """
    Create a new book with multiple authors.
    
    **Admin access required.**
    
    The book will be associated with the specified authors by their IDs.
    """
    try:
        logger.info(f"📚 Creating book: {book_data.title}")
        book = BookService.create_book(db, book_data)
        return book
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error creating book: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create book"
        )

@router.get("/", response_model=List[BookResponse])
async def list_books(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    search: Optional[str] = Query(None, description="Search books by title or description"),
    genre: Optional[str] = Query(None, description="Filter by genre"),
    author_id: Optional[int] = Query(None, description="Filter by author ID"),
    available_only: bool = Query(False, description="Show only available books"),
    db: Session = Depends(get_db)
):
    """
    Get list of all books with optional filtering and pagination.
    
    **Public endpoint - no authentication required.**
    """
    try:
        logger.info(f"📋 Fetching books (skip: {skip}, limit: {limit})")
        books = BookService.get_books(
            db=db, 
            skip=skip, 
            limit=limit, 
            search=search,
            genre=genre,
            author_id=author_id,
            available_only=available_only
        )
        return books
        
    except Exception as e:
        logger.error(f"❌ Error fetching books: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch books"
        )

@router.get("/{book_id}", response_model=BookResponse)
async def get_book(
    book_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific book by ID, including all authors.
    
    **Public endpoint - no authentication required.**
    """
    try:
        logger.info(f"🔍 Fetching book: {book_id}")
        book = BookService.get_book_by_id(db, book_id)
        
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )
        
        return book
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching book {book_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch book"
        )

@router.put("/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: int,
    book_data: BookUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)  # Only admins can update books
):
    """
    Update an existing book.
    
    **Admin access required.**
    """
    try:
        logger.info(f"✏️ Updating book: {book_id}")
        book = BookService.update_book(db, book_id, book_data)
        return book
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error updating book {book_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update book"
        )

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)  # Only admins can delete books
):
    """
    Delete a book.
    
    **Admin access required.**
    """
    try:
        logger.info(f"🗑️ Deleting book: {book_id}")
        BookService.delete_book(db, book_id)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error deleting book {book_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete book"
        )

@router.get("/search/by-author", response_model=List[BookResponse])
async def search_books_by_author(
    author_name: str = Query(..., min_length=2, description="Author name to search for"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of books to return"),
    db: Session = Depends(get_db)
):
    """
    Search books by author name.
    
    **Public endpoint - no authentication required.**
    """
    try:
        logger.info(f"🔍 Searching books by author: {author_name}")
        books = BookService.search_books_by_author(db, author_name, limit)
        return books
        
    except Exception as e:
        logger.error(f"❌ Error searching books by author: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search books by author"
        )

@router.get("/genre/{genre}", response_model=List[BookResponse])
async def get_books_by_genre(
    genre: str,
    limit: int = Query(50, ge=1, le=100, description="Maximum number of books to return"),
    db: Session = Depends(get_db)
):
    """
    Get books by genre.
    
    **Public endpoint - no authentication required.**
    """
    try:
        logger.info(f"📖 Fetching books by genre: {genre}")
        books = BookService.get_books_by_genre(db, genre, limit)
        return books
        
    except Exception as e:
        logger.error(f"❌ Error fetching books by genre: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch books by genre"
        )

@router.get("/isbn/{isbn}", response_model=BookResponse)
async def get_book_by_isbn(
    isbn: str,
    db: Session = Depends(get_db)
):
    """
    Get a book by ISBN.
    
    **Public endpoint - no authentication required.**
    """
    try:
        logger.info(f"🔍 Fetching book by ISBN: {isbn}")
        book = BookService.get_book_by_isbn(db, isbn)
        
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )
        
        return book
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching book by ISBN: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch book"
        )

@router.post("/{book_id}/borrow")
async def borrow_book(
    book_id: int,
    copies: int = Query(1, ge=1, description="Number of copies to borrow"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # Authenticated users can borrow books
):
    """
    Borrow a book (reduces available copies).
    
    **Authentication required.**
    """
    try:
        logger.info(f"📚 User {current_user.email} borrowing {copies} copy(ies) of book {book_id}")
        book = BookService.update_book_availability(db, book_id, copies)
        
        return {
            "message": f"Successfully borrowed {copies} copy(ies) of '{book.title}'",
            "available_copies": book.available_copies
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error borrowing book: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to borrow book"
        )

@router.post("/{book_id}/return")
async def return_book(
    book_id: int,
    copies: int = Query(1, ge=1, description="Number of copies to return"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # Authenticated users can return books
):
    """
    Return a book (increases available copies).
    
    **Authentication required.**
    """
    try:
        logger.info(f"📚 User {current_user.email} returning {copies} copy(ies) of book {book_id}")
        book = BookService.update_book_availability(db, book_id, -copies)  # Negative to add back
        
        return {
            "message": f"Successfully returned {copies} copy(ies) of '{book.title}'",
            "available_copies": book.available_copies
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error returning book: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to return book"
        )
