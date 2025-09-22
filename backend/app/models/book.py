
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Index, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.db import Base
from typing import Optional, Dict, List
import enum

class BookStatus(enum.Enum):
    AVAILABLE = "Available"
    CHECKED_OUT = "Checked Out"
    RESERVED = "Reserved"
    MAINTENANCE = "Maintenance"
    LOST = "Lost"
    DAMAGED = "Damaged"

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(200), nullable=False, index=True)
    isbn = Column(String(20), nullable=True, unique=True, index=True)
    genre = Column(String(50), nullable=False, index=True)
    page_count = Column(Integer, nullable=False)
    publication_year = Column(Integer, nullable=False)
    publisher = Column(String(100), nullable=True, index=True)
    language = Column(String(50), nullable=True, default="English", index=True)
    description = Column(Text, nullable=True)
    cover_image = Column(String(255), nullable=True)
    
    # Enhanced availability tracking
    is_available = Column(Boolean, nullable=False, default=True)
    total_copies = Column(Integer, nullable=False, default=1)
    available_copies = Column(Integer, nullable=False, default=1)
    reserved_copies = Column(Integer, nullable=False, default=0)
    
    # Popularity and metrics
    view_count = Column(Integer, nullable=False, default=0)
    download_count = Column(Integer, nullable=False, default=0)
    popularity_score = Column(Integer, nullable=False, default=0)
    
    # Administrative fields
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Enhanced relationships with proper cascade operations
    authors = relationship("Author", secondary="book_authors", back_populates="books")
    reviews = relationship("BookReview", back_populates="book", cascade="all, delete-orphan")
    loans = relationship("BookLoan", back_populates="book", cascade="all, delete-orphan")
    reservations = relationship("BookReservation", back_populates="book", cascade="all, delete-orphan")
    
    # Administrative relationships
    creator = relationship("User", foreign_keys=[created_by], backref="created_books")
    updater = relationship("User", foreign_keys=[updated_by], backref="updated_books")

    # Constraints and indexes
    __table_args__ = (
        CheckConstraint('publication_year >= 1000 AND publication_year <= 2100', name='valid_publication_year'),
        CheckConstraint('page_count > 0', name='positive_page_count'),
        CheckConstraint('total_copies >= 0', name='non_negative_total_copies'),
        CheckConstraint('available_copies >= 0', name='non_negative_available_copies'),
        CheckConstraint('reserved_copies >= 0', name='non_negative_reserved_copies'),
        CheckConstraint('available_copies + reserved_copies <= total_copies', name='copies_consistency'),
        Index('idx_book_title_genre', 'title', 'genre'),
        Index('idx_book_publisher_year', 'publisher', 'publication_year'),
        Index('idx_book_availability', 'is_available', 'available_copies'),
        Index('idx_book_popularity', 'popularity_score', 'view_count'),
        Index('idx_book_created_at', 'created_at'),
    )

    @property
    def average_rating(self) -> float:
        """Calculate average rating from all reviews"""
        if not self.reviews:
            return 0.0
        total_rating = sum(review.rating for review in self.reviews)
        return round(total_rating / len(self.reviews), 1)

    @property
    def review_count(self) -> int:
        """Get total number of reviews"""
        return len(self.reviews) if self.reviews else 0

    @property
    def rating_distribution(self) -> Dict[int, int]:
        """Get distribution of ratings (1-5 stars)"""
        if not self.reviews:
            return {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for review in self.reviews:
            distribution[review.rating] += 1
        return distribution

    @property
    def author_names(self) -> List[str]:
        """Get list of author names"""
        return [author.full_name for author in self.authors] if self.authors else []

    @property
    def is_popular(self) -> bool:
        """Check if book is considered popular"""
        return self.popularity_score > 100 or self.review_count > 10

    @property
    def availability_status(self) -> str:
        """Get current availability status"""
        if not self.is_available:
            return "Unavailable"
        elif self.available_copies == 0:
            return "All copies checked out"
        elif self.available_copies <= 2:
            return "Limited availability"
        else:
            return "Available"

    def can_be_borrowed(self) -> bool:
        """Check if book can be borrowed"""
        return self.is_available and self.available_copies > 0

    def can_be_reserved(self) -> bool:
        """Check if book can be reserved"""
        return self.is_available and self.total_copies > 0

    def update_popularity_score(self):
        """Update popularity score based on various metrics"""
        score = 0
        score += self.view_count * 1
        score += self.download_count * 2
        score += self.review_count * 5
        score += int(self.average_rating * 10)
        self.popularity_score = score

    def increment_view_count(self):
        """Increment view count and update popularity"""
        self.view_count += 1
        self.update_popularity_score()

    def increment_download_count(self):
        """Increment download count and update popularity"""
        self.download_count += 1
        self.update_popularity_score()

    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "title": self.title,
            "isbn": self.isbn,
            "genre": self.genre,
            "page_count": self.page_count,
            "publication_year": self.publication_year,
            "publisher": self.publisher,
            "language": self.language,
            "description": self.description,
            "cover_image": self.cover_image,
            "is_available": self.is_available,
            "total_copies": self.total_copies,
            "available_copies": self.available_copies,
            "reserved_copies": self.reserved_copies,
            "view_count": self.view_count,
            "download_count": self.download_count,
            "popularity_score": self.popularity_score,
            "average_rating": self.average_rating,
            "review_count": self.review_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "authors": [author.to_dict() if hasattr(author, 'to_dict') else {"id": author.id, "name": author.name} for author in self.authors] if self.authors else []
        }

    def __repr__(self):
        return f"<Book(id={self.id}, title='{self.title}', avg_rating={self.average_rating}, copies={self.available_copies}/{self.total_copies})>"