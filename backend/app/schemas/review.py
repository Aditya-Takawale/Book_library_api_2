from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime

class ReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")
    review_text: Optional[str] = Field(None, max_length=2000, description="Review text content")
    title: Optional[str] = Field(None, max_length=200, description="Review title")
    is_spoiler: Optional[bool] = Field(False, description="Whether review contains spoilers")

    @validator('review_text')
    def validate_review_text(cls, v):
        if v and len(v.strip()) < 10:
            raise ValueError('Review text must be at least 10 characters long')
        return v.strip() if v else v

    @validator('title')
    def validate_title(cls, v):
        if v and len(v.strip()) < 3:
            raise ValueError('Review title must be at least 3 characters long')
        return v.strip() if v else v

class ReviewCreate(ReviewBase):
    """Schema for creating a new review"""
    pass

class ReviewUpdate(BaseModel):
    """Schema for updating an existing review"""
    rating: Optional[int] = Field(None, ge=1, le=5)
    review_text: Optional[str] = Field(None, max_length=2000)
    title: Optional[str] = Field(None, max_length=200)
    is_spoiler: Optional[bool] = None

    @validator('review_text')
    def validate_review_text(cls, v):
        if v is not None and len(v.strip()) < 10:
            raise ValueError('Review text must be at least 10 characters long')
        return v.strip() if v else v

class UserSummary(BaseModel):
    """User information for review display"""
    id: int
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    class Config:
        from_attributes = True

class ReviewResponse(ReviewBase):
    """Complete review information response"""
    id: int
    book_id: int
    user_id: int
    user: UserSummary
    is_verified_purchase: bool = False
    helpful_votes: int = 0
    total_votes: int = 0
    helpfulness_ratio: float = 0.0
    is_helpful: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ReviewSummary(BaseModel):
    """Lightweight review for book listings"""
    id: int
    rating: int
    title: Optional[str] = None
    review_text: Optional[str] = None
    user: UserSummary
    helpful_votes: int = 0
    is_helpful: bool = False
    created_at: datetime

    class Config:
        from_attributes = True

class ReviewWithBook(ReviewResponse):
    """Review with book information"""
    book_title: str
    book_id: int

    class Config:
        from_attributes = True

class ReviewStats(BaseModel):
    """Review statistics for a book"""
    total_reviews: int = 0
    average_rating: float = 0.0
    rating_distribution: Dict[int, int] = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    helpful_reviews_count: int = 0
    verified_reviews_count: int = 0

class BookWithReviews(BaseModel):
    """Book information with reviews"""
    id: int
    title: str
    author: str  # For backward compatibility
    genre: str
    average_rating: float = 0.0
    review_count: int = 0
    rating_distribution: Dict[int, int] = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    recent_reviews: List[ReviewSummary] = []
    
    class Config:
        from_attributes = True

class ReviewVoteCreate(BaseModel):
    """Schema for voting on review helpfulness"""
    is_helpful: bool = Field(..., description="True if review is helpful, False if not")

class ReviewVoteResponse(BaseModel):
    """Response for review vote"""
    id: int
    review_id: int
    user_id: int
    is_helpful: bool
    created_at: datetime

    class Config:
        from_attributes = True

class ReviewAnalytics(BaseModel):
    """Comprehensive review analytics"""
    total_reviews: int
    average_rating: float
    rating_distribution: Dict[str, int]
    reviews_this_month: int
    top_reviewers: List[Dict[str, Any]]
    most_helpful_reviews: List[ReviewSummary]
    recent_reviews: List[ReviewSummary]
