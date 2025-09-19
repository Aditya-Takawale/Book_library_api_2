from sqlalchemy import Column, Integer, String, Text, DateTime, Table, ForeignKey, Date, Index, CheckConstraint, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.db import Base
from datetime import date
from typing import List, Optional

# Association table for many-to-many relationship between books and authors
book_author_association = Table(
    'book_authors',
    Base.metadata,
    Column('book_id', Integer, ForeignKey('books.id', ondelete='CASCADE'), primary_key=True),
    Column('author_id', Integer, ForeignKey('authors.id', ondelete='CASCADE'), primary_key=True),
    Column('role', String(50), default='Author'),  # Author, Co-author, Editor, Translator, etc.
    Column('order', Integer, default=1),  # Order of authors for multi-author books
    Column('created_at', DateTime, server_default=func.now())
)

class Author(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    full_name = Column(String(200), nullable=False, index=True)  # Computed field for easier searching
    bio = Column(Text, nullable=True)
    birth_date = Column(Date, nullable=True)  # Full birth date for precision
    death_date = Column(Date, nullable=True)  # Full death date for precision
    birth_year = Column(Integer, nullable=True)  # Backward compatibility
    death_year = Column(Integer, nullable=True)  # Backward compatibility
    nationality = Column(String(100), nullable=True, index=True)
    birth_place = Column(String(200), nullable=True)  # City, Country
    education = Column(Text, nullable=True)  # Educational background
    awards = Column(Text, nullable=True)  # Literary awards and honors
    genres = Column(String(500), nullable=True)  # Primary writing genres (comma-separated)
    website = Column(String(255), nullable=True)
    wikipedia_url = Column(String(255), nullable=True)  # Wikipedia page link
    social_media = Column(Text, nullable=True)  # JSON string for social media links
    is_living = Column(Boolean, default=True, nullable=False)  # True for living, False for deceased
    
    # Administrative fields
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Enhanced relationships with proper cascade operations
    books = relationship("Book", secondary=book_author_association, back_populates="authors")
    
    # Administrative relationships
    creator = relationship("User", foreign_keys=[created_by], backref="created_authors")
    updater = relationship("User", foreign_keys=[updated_by], backref="updated_authors")

    # Constraints and indexes
    __table_args__ = (
        CheckConstraint('birth_year IS NULL OR (birth_year >= 1000 AND birth_year <= 2100)', name='valid_birth_year'),
        CheckConstraint('death_year IS NULL OR (death_year >= 1000 AND death_year <= 2100)', name='valid_death_year'),
        CheckConstraint('death_year IS NULL OR birth_year IS NULL OR death_year >= birth_year', name='death_after_birth'),
        Index('idx_author_name_nationality', 'full_name', 'nationality'),
        Index('idx_author_birth_year', 'birth_year'),
        Index('idx_author_is_living', 'is_living'),
        Index('idx_author_created_at', 'created_at'),
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if 'first_name' in kwargs and 'last_name' in kwargs:
            self.full_name = f"{kwargs['first_name']} {kwargs['last_name']}"
        
        # Auto-populate year fields from date fields if provided
        if 'birth_date' in kwargs and kwargs['birth_date']:
            self.birth_year = kwargs['birth_date'].year
        if 'death_date' in kwargs and kwargs['death_date']:
            self.death_year = kwargs['death_date'].year
            self.is_living = False
            self.death_year = kwargs['death_date'].year
            self.is_living = 0

    @property
    def age(self) -> int:
        """Calculate current age or age at death"""
        if self.birth_date:
            end_date = self.death_date if self.death_date else date.today()
            return end_date.year - self.birth_date.year - (
                (end_date.month, end_date.day) < (self.birth_date.month, self.birth_date.day)
            )
        return None

    @property
    def years_active(self) -> str:
        """Return a string representation of years active"""
        if self.birth_year:
            start = self.birth_year + 20  # Assume started writing around age 20
            end = self.death_year if self.death_year else "present"
            return f"{start}-{end}"
        return "Unknown"

    def __repr__(self):
        return f"<Author(id={self.id}, full_name='{self.full_name}', nationality='{self.nationality}')>"
