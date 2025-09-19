from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.db import Base

class BookReview(Base):
    __tablename__ = "book_reviews"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5 stars
    review_text = Column(Text, nullable=True)
    title = Column(String(200), nullable=True)  # Optional review title
    is_spoiler = Column(Integer, default=0)  # 1 if contains spoilers, 0 if not
    is_verified_purchase = Column(Integer, default=0)  # 1 if user has borrowed/purchased book
    helpful_votes = Column(Integer, default=0)  # Number of helpful votes
    total_votes = Column(Integer, default=0)  # Total votes received
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    book = relationship("Book", back_populates="reviews")
    user = relationship("User", back_populates="reviews")
    votes = relationship("ReviewVote", back_populates="review", cascade="all, delete-orphan")

    # Indexes for performance
    __table_args__ = (
        Index('idx_book_reviews_book_id', 'book_id'),
        Index('idx_book_reviews_user_id', 'user_id'),
        Index('idx_book_reviews_rating', 'rating'),
        Index('idx_book_reviews_created_at', 'created_at'),
        Index('idx_book_reviews_book_user', 'book_id', 'user_id', unique=True),  # One review per user per book
    )

    @property
    def helpfulness_ratio(self) -> float:
        """Calculate helpfulness ratio (helpful votes / total votes)"""
        if self.total_votes == 0:
            return 0.0
        return round(self.helpful_votes / self.total_votes, 2)

    @property
    def is_helpful(self) -> bool:
        """Determine if review is considered helpful (>60% helpful ratio with min 3 votes)"""
        return self.total_votes >= 3 and self.helpfulness_ratio >= 0.6

    def __repr__(self):
        return f"<BookReview(id={self.id}, book_id={self.book_id}, user_id={self.user_id}, rating={self.rating})>"


class ReviewVote(Base):
    __tablename__ = "review_votes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    review_id = Column(Integer, ForeignKey("book_reviews.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    is_helpful = Column(Integer, nullable=False)  # 1 for helpful, 0 for not helpful
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    review = relationship("BookReview", back_populates="votes")
    user = relationship("User", back_populates="review_votes")

    # Indexes for performance
    __table_args__ = (
        Index('idx_review_votes_review_id', 'review_id'),
        Index('idx_review_votes_user_id', 'user_id'),
        Index('idx_review_votes_review_user', 'review_id', 'user_id', unique=True),  # One vote per user per review
    )

    def __repr__(self):
        return f"<ReviewVote(id={self.id}, review_id={self.review_id}, user_id={self.user_id}, is_helpful={self.is_helpful})>"
