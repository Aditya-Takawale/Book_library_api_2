from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_
from fastapi import HTTPException, status
from app.models.author import Author
from app.schemas.author import AuthorCreate, AuthorUpdate
from typing import List, Optional
import logging
import json
from datetime import date

logger = logging.getLogger("BookLibraryAPI")

class AuthorService:
    
    @staticmethod
    def create_author(db: Session, author_data: AuthorCreate) -> Author:
        """Create a new author with comprehensive biographical information"""
        try:
            # Check if author already exists (by full name)
            full_name = f"{author_data.first_name} {author_data.last_name}"
            existing_author = db.query(Author).filter(Author.full_name == full_name).first()
            
            if existing_author:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Author '{full_name}' already exists"
                )
            
            # Prepare author data
            author_dict = author_data.dict(exclude_unset=True)
            
            # Auto-populate year fields from date fields if not provided
            if author_data.birth_date and not author_data.birth_year:
                author_dict['birth_year'] = author_data.birth_date.year
            
            if author_data.death_date and not author_data.death_year:
                author_dict['death_year'] = author_data.death_date.year
                author_dict['is_living'] = 0
            
            # Create new author
            db_author = Author(
                first_name=author_data.first_name,
                last_name=author_data.last_name,
                full_name=full_name,
                **author_dict
            )
            
            db.add(db_author)
            db.commit()
            db.refresh(db_author)
            
            logger.info(f"✅ Author created successfully: {full_name} (ID: {db_author.id})")
            return db_author
            
        except IntegrityError as e:
            db.rollback()
            logger.error(f"❌ Database integrity error creating author: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create author due to data constraints"
            )
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Error creating author: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create author"
            )
    
    @staticmethod
    def get_author_by_id(db: Session, author_id: int) -> Optional[Author]:
        """Get author by ID"""
        return db.query(Author).filter(Author.id == author_id).first()
    
    @staticmethod
    def get_author_by_name(db: Session, full_name: str) -> Optional[Author]:
        """Get author by full name"""
        return db.query(Author).filter(Author.full_name.ilike(f"%{full_name}%")).first()
    
    @staticmethod
    def get_authors(db: Session, skip: int = 0, limit: int = 100, search: str = None, 
                   nationality: str = None, is_living: bool = None, 
                   birth_year_start: int = None, birth_year_end: int = None) -> List[Author]:
        """Get all authors with advanced filtering options"""
        query = db.query(Author)
        
        # Text search
        if search:
            query = query.filter(
                or_(
                    Author.full_name.ilike(f"%{search}%"),
                    Author.first_name.ilike(f"%{search}%"),
                    Author.last_name.ilike(f"%{search}%"),
                    Author.bio.ilike(f"%{search}%"),
                    Author.nationality.ilike(f"%{search}%"),
                    Author.genres.ilike(f"%{search}%")
                )
            )
        
        # Nationality filter
        if nationality:
            query = query.filter(Author.nationality.ilike(f"%{nationality}%"))
        
        # Living status filter
        if is_living is not None:
            query = query.filter(Author.is_living == (1 if is_living else 0))
        
        # Birth year range filter
        if birth_year_start:
            query = query.filter(Author.birth_year >= birth_year_start)
        if birth_year_end:
            query = query.filter(Author.birth_year <= birth_year_end)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_authors_by_nationality(db: Session, nationality: str) -> List[Author]:
        """Get all authors from a specific nationality"""
        return db.query(Author).filter(Author.nationality.ilike(f"%{nationality}%")).all()
    
    @staticmethod
    def get_living_authors(db: Session) -> List[Author]:
        """Get all living authors"""
        return db.query(Author).filter(Author.is_living == 1).all()
    
    @staticmethod
    def get_authors_by_genre(db: Session, genre: str) -> List[Author]:
        """Get authors who write in a specific genre"""
        return db.query(Author).filter(Author.genres.ilike(f"%{genre}%")).all()
    
    @staticmethod
    def get_authors_by_birth_decade(db: Session, decade: int) -> List[Author]:
        """Get authors born in a specific decade (e.g., 1950 for 1950s)"""
        start_year = decade
        end_year = decade + 9
        return db.query(Author).filter(
            and_(Author.birth_year >= start_year, Author.birth_year <= end_year)
        ).all()
    
    @staticmethod
    def update_author(db: Session, author_id: int, author_data: AuthorUpdate) -> Author:
        """Update an existing author with biographical information"""
        try:
            author = AuthorService.get_author_by_id(db, author_id)
            if not author:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Author not found"
                )
            
            # Update fields if provided
            update_data = author_data.dict(exclude_unset=True)
            
            # Update full_name if first_name or last_name changed
            if 'first_name' in update_data or 'last_name' in update_data:
                first_name = update_data.get('first_name', author.first_name)
                last_name = update_data.get('last_name', author.last_name)
                update_data['full_name'] = f"{first_name} {last_name}"
            
            # Auto-populate year fields from date fields if provided
            if 'birth_date' in update_data and update_data['birth_date']:
                update_data['birth_year'] = update_data['birth_date'].year
                
            if 'death_date' in update_data and update_data['death_date']:
                update_data['death_year'] = update_data['death_date'].year
                update_data['is_living'] = 0
            elif 'is_living' in update_data and update_data['is_living'] == 1:
                # If marked as living, clear death information
                update_data['death_date'] = None
                update_data['death_year'] = None
            
            for field, value in update_data.items():
                setattr(author, field, value)
            
            db.commit()
            db.refresh(author)
            
            logger.info(f"✅ Author updated successfully: {author.full_name} (ID: {author.id})")
            return author
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Error updating author {author_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update author"
            )
    
    @staticmethod
    def update_author_social_media(db: Session, author_id: int, social_media_data: dict) -> Author:
        """Update author's social media links"""
        try:
            author = AuthorService.get_author_by_id(db, author_id)
            if not author:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Author not found"
                )
            
            # Convert dict to JSON string
            author.social_media = json.dumps(social_media_data)
            
            db.commit()
            db.refresh(author)
            
            logger.info(f"✅ Author social media updated: {author.full_name} (ID: {author.id})")
            return author
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Error updating author social media {author_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update author social media"
            )
    
    @staticmethod
    def delete_author(db: Session, author_id: int) -> bool:
        """Delete an author"""
        try:
            author = AuthorService.get_author_by_id(db, author_id)
            if not author:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Author not found"
                )
            
            # Check if author has associated books
            if author.books:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot delete author '{author.full_name}' - they have {len(author.books)} associated books"
                )
            
            db.delete(author)
            db.commit()
            
            logger.info(f"✅ Author deleted successfully: {author.full_name} (ID: {author.id})")
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Error deleting author {author_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete author"
            )
    
    @staticmethod
    def get_authors_by_ids(db: Session, author_ids: List[int]) -> List[Author]:
        """Get multiple authors by their IDs"""
        authors = db.query(Author).filter(Author.id.in_(author_ids)).all()
        found_ids = [author.id for author in authors]
        missing_ids = [author_id for author_id in author_ids if author_id not in found_ids]
        
        if missing_ids:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Authors not found with IDs: {missing_ids}"
            )
        
        return authors
    
    @staticmethod
    def get_author_statistics(db: Session) -> dict:
        """Get comprehensive author statistics"""
        total_authors = db.query(Author).count()
        living_authors = db.query(Author).filter(Author.is_living == 1).count()
        deceased_authors = db.query(Author).filter(Author.is_living == 0).count()
        
        # Get nationality distribution
        nationality_stats = db.query(Author.nationality).filter(Author.nationality.isnot(None)).all()
        nationality_counts = {}
        for (nationality,) in nationality_stats:
            nationality_counts[nationality] = nationality_counts.get(nationality, 0) + 1
        
        return {
            "total_authors": total_authors,
            "living_authors": living_authors,
            "deceased_authors": deceased_authors,
            "nationality_distribution": nationality_counts,
            "completion_stats": {
                "with_bio": db.query(Author).filter(Author.bio.isnot(None)).count(),
                "with_birth_date": db.query(Author).filter(Author.birth_date.isnot(None)).count(),
                "with_nationality": db.query(Author).filter(Author.nationality.isnot(None)).count(),
                "with_education": db.query(Author).filter(Author.education.isnot(None)).count(),
                "with_awards": db.query(Author).filter(Author.awards.isnot(None)).count()
            }
        }
