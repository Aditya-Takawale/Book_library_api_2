from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.book import Book
from app.models.author import Author
from app.schemas.book import BookCreate, BookUpdate
from app.services.author_service import AuthorService
from typing import List, Optional
import logging

logger = logging.getLogger("BookLibraryAPI")

class BookService:
    
    @staticmethod
    def create_book(db: Session, book_data: BookCreate) -> Book:
        """Create a new book with multiple authors"""
        try:
            # Validate authors exist
            authors = AuthorService.get_authors_by_ids(db, book_data.author_ids)
            
            # Check for duplicate ISBN if provided
            if book_data.isbn:
                existing_book = db.query(Book).filter(Book.isbn == book_data.isbn).first()
                if existing_book:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Book with ISBN '{book_data.isbn}' already exists"
                    )
            
            # Create book record
            book_dict = book_data.dict(exclude={'author_ids'})
            db_book = Book(**book_dict)
            
            # Set availability based on copies
            db_book.is_available = book_data.available_copies > 0
            
            # Associate authors
            db_book.authors = authors
            
            db.add(db_book)
            db.commit()
            db.refresh(db_book)
            
            author_names = [author.full_name for author in authors]
            logger.info(f"✅ Book created successfully: '{db_book.title}' by {', '.join(author_names)} (ID: {db_book.id})")
            return db_book
            
        except HTTPException:
            db.rollback()
            raise
        except IntegrityError as e:
            db.rollback()
            logger.error(f"❌ Database integrity error creating book: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create book due to data constraints"
            )
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Error creating book: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create book"
            )
    
    @staticmethod
    def get_book_by_id(db: Session, book_id: int) -> Optional[Book]:
        """Get book by ID with authors"""
        return db.query(Book).filter(Book.id == book_id).first()
    
    @staticmethod
    def get_book_by_isbn(db: Session, isbn: str) -> Optional[Book]:
        """Get book by ISBN"""
        return db.query(Book).filter(Book.isbn == isbn).first()
    
    @staticmethod
    def get_books(
        db: Session, 
        skip: int = 0, 
        limit: int = 100, 
        search: str = None,
        genre: str = None,
        author_id: int = None,
        available_only: bool = False
    ) -> List[Book]:
        """Get books with optional filtering and pagination"""
        query = db.query(Book)
        
        # Apply filters
        if search:
            query = query.filter(
                Book.title.ilike(f"%{search}%") |
                Book.description.ilike(f"%{search}%")
            )
        
        if genre:
            query = query.filter(Book.genre.ilike(f"%{genre}%"))
        
        if author_id:
            query = query.join(Book.authors).filter(Author.id == author_id)
        
        if available_only:
            query = query.filter(Book.available_copies > 0)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update_book(db: Session, book_id: int, book_data: BookUpdate) -> Book:
        """Update an existing book"""
        try:
            book = BookService.get_book_by_id(db, book_id)
            if not book:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Book not found"
                )
            
            # Check ISBN uniqueness if being updated
            if book_data.isbn and book_data.isbn != book.isbn:
                existing_book = db.query(Book).filter(Book.isbn == book_data.isbn).first()
                if existing_book:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Book with ISBN '{book_data.isbn}' already exists"
                    )
            
            # Update authors if provided
            if book_data.author_ids is not None:
                authors = AuthorService.get_authors_by_ids(db, book_data.author_ids)
                book.authors = authors
            
            # Update other fields
            update_data = book_data.dict(exclude_unset=True, exclude={'author_ids'})
            for field, value in update_data.items():
                setattr(book, field, value)
            
            # Update availability based on copies
            if 'available_copies' in update_data:
                book.is_available = book.available_copies > 0
            
            db.commit()
            db.refresh(book)
            
            logger.info(f"✅ Book updated successfully: '{book.title}' (ID: {book.id})")
            return book
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Error updating book {book_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update book"
            )
    
    @staticmethod
    def delete_book(db: Session, book_id: int) -> bool:
        """Delete a book"""
        try:
            book = BookService.get_book_by_id(db, book_id)
            if not book:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Book not found"
                )
            
            db.delete(book)
            db.commit()
            
            logger.info(f"✅ Book deleted successfully: '{book.title}' (ID: {book.id})")
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Error deleting book {book_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete book"
            )
    
    @staticmethod
    def search_books_by_author(db: Session, author_name: str, limit: int = 50) -> List[Book]:
        """Search books by author name"""
        return (
            db.query(Book)
            .join(Book.authors)
            .filter(Author.full_name.ilike(f"%{author_name}%"))
            .limit(limit)
            .all()
        )
    
    @staticmethod
    def get_books_by_genre(db: Session, genre: str, limit: int = 50) -> List[Book]:
        """Get books by genre"""
        return (
            db.query(Book)
            .filter(Book.genre.ilike(f"%{genre}%"))
            .limit(limit)
            .all()
        )
    
    @staticmethod
    def update_book_availability(db: Session, book_id: int, copies_borrowed: int = 1) -> Book:
        """Update book availability when borrowed/returned"""
        try:
            book = BookService.get_book_by_id(db, book_id)
            if not book:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Book not found"
                )
            
            new_available = book.available_copies - copies_borrowed
            if new_available < 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Not enough copies available"
                )
            
            book.available_copies = new_available
            book.is_available = new_available > 0
            
            db.commit()
            db.refresh(book)
            
            action = "borrowed" if copies_borrowed > 0 else "returned"
            logger.info(f"✅ Book {action}: '{book.title}' - Available copies: {book.available_copies}")
            return book
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Error updating book availability {book_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update book availability"
            )
