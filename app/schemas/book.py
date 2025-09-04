
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Book title")
    isbn: Optional[str] = Field(None, max_length=20, description="ISBN number")
    genre: str = Field(..., min_length=1, max_length=50, description="Book genre")
    page_count: int = Field(..., gt=0, description="Number of pages")
    publication_year: int = Field(..., ge=1, le=2030, description="Year of publication")
    publisher: Optional[str] = Field(None, max_length=100, description="Publisher name")
    language: Optional[str] = Field("English", max_length=50, description="Book language")
    description: Optional[str] = Field(None, description="Book description")
    cover_image: Optional[str] = Field(None, max_length=255, description="Cover image URL")
    total_copies: int = Field(1, gt=0, description="Total number of copies")
    available_copies: int = Field(1, ge=0, description="Number of available copies")

    @validator('available_copies')
    def validate_available_copies(cls, v, values):
        if 'total_copies' in values and v > values['total_copies']:
            raise ValueError('Available copies cannot exceed total copies')
        return v

class BookCreate(BookBase):
    author_ids: List[int] = Field(..., min_items=1, description="List of author IDs")

class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    isbn: Optional[str] = Field(None, max_length=20)
    genre: Optional[str] = Field(None, min_length=1, max_length=50)
    page_count: Optional[int] = Field(None, gt=0)
    publication_year: Optional[int] = Field(None, ge=1, le=2030)
    publisher: Optional[str] = Field(None, max_length=100)
    language: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    cover_image: Optional[str] = Field(None, max_length=255)
    total_copies: Optional[int] = Field(None, gt=0)
    available_copies: Optional[int] = Field(None, ge=0)
    author_ids: Optional[List[int]] = Field(None, min_items=1, description="List of author IDs")

# Import here to avoid circular imports
from .author import AuthorSummary

class BookResponse(BookBase):
    id: int
    is_available: bool
    authors: List[AuthorSummary] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class BookSummary(BaseModel):
    """Lightweight book representation for author listings"""
    id: int
    title: str
    genre: str
    publication_year: int
    authors: List[AuthorSummary] = []

    class Config:
        from_attributes = True

class BookWithDetails(BookResponse):
    """Extended book information with full details"""
    pass

# Legacy support for existing API (backward compatibility)
class Book(BookResponse):
    """Legacy book model for backward compatibility"""
    pass