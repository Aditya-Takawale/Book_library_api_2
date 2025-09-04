from pydantic import BaseModel, Field, validator, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime, date
import json

class AuthorBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100, description="Author's first name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Author's last name")
    bio: Optional[str] = Field(None, description="Author biography")
    birth_date: Optional[date] = Field(None, description="Author's exact birth date")
    death_date: Optional[date] = Field(None, description="Author's exact death date (if applicable)")
    birth_year: Optional[int] = Field(None, ge=1, le=2024, description="Author's birth year (for backward compatibility)")
    death_year: Optional[int] = Field(None, ge=1, le=2024, description="Author's death year (for backward compatibility)")
    nationality: Optional[str] = Field(None, max_length=100, description="Author's nationality")
    birth_place: Optional[str] = Field(None, max_length=200, description="Author's birth place (City, Country)")
    education: Optional[str] = Field(None, description="Educational background")
    awards: Optional[str] = Field(None, description="Literary awards and honors")
    genres: Optional[str] = Field(None, max_length=500, description="Primary writing genres (comma-separated)")
    website: Optional[str] = Field(None, max_length=255, description="Author's official website")
    wikipedia_url: Optional[str] = Field(None, max_length=255, description="Wikipedia page URL")
    social_media: Optional[str] = Field(None, description="Social media links (JSON format)")
    is_living: Optional[int] = Field(1, description="1 for living, 0 for deceased")

    @validator('death_date')
    def validate_death_date(cls, v, values):
        if v is not None and 'birth_date' in values and values['birth_date'] is not None:
            if v <= values['birth_date']:
                raise ValueError('Death date must be after birth date')
        return v

    @validator('death_year')
    def validate_death_year(cls, v, values):
        if v is not None and 'birth_year' in values and values['birth_year'] is not None:
            if v <= values['birth_year']:
                raise ValueError('Death year must be after birth year')
        return v

    @validator('website', 'wikipedia_url')
    def validate_urls(cls, v):
        if v and not (v.startswith('http://') or v.startswith('https://')):
            return f"https://{v}"
        return v

    @validator('social_media')
    def validate_social_media(cls, v):
        if v:
            try:
                # Validate if it's proper JSON
                json.loads(v)
            except json.JSONDecodeError:
                raise ValueError('Social media must be valid JSON format')
        return v

class AuthorCreate(AuthorBase):
    """Schema for creating a new author"""
    pass

class AuthorUpdate(BaseModel):
    """Schema for updating author information"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    bio: Optional[str] = None
    birth_date: Optional[date] = None
    death_date: Optional[date] = None
    birth_year: Optional[int] = Field(None, ge=1, le=2024)
    death_year: Optional[int] = Field(None, ge=1, le=2024)
    nationality: Optional[str] = Field(None, max_length=100)
    birth_place: Optional[str] = Field(None, max_length=200)
    education: Optional[str] = None
    awards: Optional[str] = None
    genres: Optional[str] = Field(None, max_length=500)
    website: Optional[str] = Field(None, max_length=255)
    wikipedia_url: Optional[str] = Field(None, max_length=255)
    social_media: Optional[str] = None
    is_living: Optional[int] = Field(None, description="1 for living, 0 for deceased")

    @validator('website', 'wikipedia_url')
    def validate_urls(cls, v):
        if v and not (v.startswith('http://') or v.startswith('https://')):
            return f"https://{v}"
        return v

class AuthorResponse(AuthorBase):
    """Complete author information response"""
    id: int
    full_name: str
    age: Optional[int] = Field(None, description="Current age or age at death")
    years_active: Optional[str] = Field(None, description="Years active as a writer")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AuthorSummary(BaseModel):
    """Lightweight author representation for book listings"""
    id: int
    full_name: str
    nationality: Optional[str] = None

    class Config:
        from_attributes = True

class AuthorBiographical(BaseModel):
    """Detailed biographical information"""
    id: int
    full_name: str
    bio: Optional[str] = None
    birth_date: Optional[date] = None
    death_date: Optional[date] = None
    nationality: Optional[str] = None
    birth_place: Optional[str] = None
    education: Optional[str] = None
    awards: Optional[str] = None
    genres: Optional[str] = None
    age: Optional[int] = None
    years_active: Optional[str] = None
    is_living: Optional[int] = None

    class Config:
        from_attributes = True

class AuthorWithBooks(AuthorResponse):
    """Author with associated books"""
    books: List['BookSummary'] = []

    class Config:
        from_attributes = True

# Forward reference for book summary (to avoid circular imports)
class BookSummary(BaseModel):
    id: int
    title: str
    genre: str
    publication_year: int

    class Config:
        from_attributes = True

# Update the forward reference
AuthorWithBooks.model_rebuild()
