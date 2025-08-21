from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    author: str = Field(..., min_length=1, max_length=100)
    genre: str = Field(..., min_length=1, max_length=50)
    page_count: int = Field(..., gt=0)
    publication_year: int = Field(..., ge=1000, le=datetime.now().year)
    description: Optional[str] = Field(None, max_length=1000)
    cover_image: Optional[str] = None

    @validator("title", "author", "genre")
    def strip_strings(cls, v):
        return v.strip() if v else v

class BookCreate(BookBase):
    pass

class BookUpdate(BookBase):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    author: Optional[str] = Field(None, min_length=1, max_length=100)
    genre: Optional[str] = Field(None, min_length=1, max_length=50)
    page_count: Optional[int] = Field(None, gt=0)
    publication_year: Optional[int] = Field(None, ge=1000, le=datetime.now().year)

class BookResponse(BookBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True