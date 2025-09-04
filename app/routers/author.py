from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.database import get_db
from app.schemas.author import (AuthorCreate, AuthorUpdate, AuthorResponse, AuthorWithBooks, 
                               AuthorSummary, AuthorBiographical)
from app.services.author_service import AuthorService
from app.utils.dependencies import get_admin_user, get_current_user
import logging

logger = logging.getLogger("BookLibraryAPI")

router = APIRouter(prefix="/authors", tags=["Authors"])

@router.post("/", response_model=AuthorResponse, status_code=status.HTTP_201_CREATED)
async def create_author(
    author_data: AuthorCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)  # Only admins can create authors
):
    """
    Create a new author with comprehensive biographical information.
    
    **Admin access required.**
    
    **New Features:**
    - Full birth/death dates (not just years)
    - Birth place and nationality
    - Educational background
    - Awards and honors
    - Writing genres
    - Social media links
    - Wikipedia URL
    """
    try:
        logger.info(f"📝 Creating author: {author_data.first_name} {author_data.last_name}")
        author = AuthorService.create_author(db, author_data)
        return author
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error creating author: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create author"
        )

@router.get("/", response_model=List[AuthorResponse])
async def list_authors(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    search: Optional[str] = Query(None, description="Search authors by name, bio, nationality, or genres"),
    nationality: Optional[str] = Query(None, description="Filter by nationality"),
    is_living: Optional[bool] = Query(None, description="Filter by living status"),
    birth_year_start: Optional[int] = Query(None, description="Filter by birth year (start)"),
    birth_year_end: Optional[int] = Query(None, description="Filter by birth year (end)"),
    db: Session = Depends(get_db)
):
    """
    Get list of all authors with advanced filtering options.
    
    **Public endpoint - no authentication required.**
    
    **Enhanced Features:**
    - Search across bio, nationality, and genres
    - Filter by nationality
    - Filter by living status
    - Filter by birth year range
    """
    try:
        logger.info(f"📋 Fetching authors with filters - skip: {skip}, limit: {limit}")
        authors = AuthorService.get_authors(
            db, skip=skip, limit=limit, search=search,
            nationality=nationality, is_living=is_living,
            birth_year_start=birth_year_start, birth_year_end=birth_year_end
        )
        return authors
        
    except Exception as e:
        logger.error(f"❌ Error fetching authors: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch authors"
        )

@router.get("/statistics", response_model=Dict[str, Any])
async def get_author_statistics(
    db: Session = Depends(get_db)
):
    """
    Get comprehensive author statistics and analytics.
    
    **Public endpoint - no authentication required.**
    
    **Returns:**
    - Total author count
    - Living vs deceased counts
    - Nationality distribution
    - Data completion statistics
    """
    try:
        logger.info("� Fetching author statistics")
        stats = AuthorService.get_author_statistics(db)
        return stats
        
    except Exception as e:
        logger.error(f"❌ Error fetching author statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch author statistics"
        )

@router.get("/nationality/{nationality}", response_model=List[AuthorSummary])
async def get_authors_by_nationality(
    nationality: str,
    db: Session = Depends(get_db)
):
    """
    Get all authors from a specific nationality.
    
    **Public endpoint - no authentication required.**
    """
    try:
        logger.info(f"🌍 Fetching authors by nationality: {nationality}")
        authors = AuthorService.get_authors_by_nationality(db, nationality)
        return authors
        
    except Exception as e:
        logger.error(f"❌ Error fetching authors by nationality: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch authors by nationality"
        )

@router.get("/living", response_model=List[AuthorSummary])
async def get_living_authors(
    db: Session = Depends(get_db)
):
    """
    Get all living authors.
    
    **Public endpoint - no authentication required.**
    """
    try:
        logger.info("👥 Fetching living authors")
        authors = AuthorService.get_living_authors(db)
        return authors
        
    except Exception as e:
        logger.error(f"❌ Error fetching living authors: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch living authors"
        )

@router.get("/genre/{genre}", response_model=List[AuthorSummary])
async def get_authors_by_genre(
    genre: str,
    db: Session = Depends(get_db)
):
    """
    Get authors who write in a specific genre.
    
    **Public endpoint - no authentication required.**
    """
    try:
        logger.info(f"📚 Fetching authors by genre: {genre}")
        authors = AuthorService.get_authors_by_genre(db, genre)
        return authors
        
    except Exception as e:
        logger.error(f"❌ Error fetching authors by genre: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch authors by genre"
        )

@router.get("/decade/{decade}", response_model=List[AuthorSummary])
async def get_authors_by_birth_decade(
    decade: int,
    db: Session = Depends(get_db)
):
    """
    Get authors born in a specific decade.
    
    **Public endpoint - no authentication required.**
    
    **Example:** `/authors/decade/1950` returns authors born in the 1950s
    """
    try:
        logger.info(f"📅 Fetching authors by birth decade: {decade}")
        authors = AuthorService.get_authors_by_birth_decade(db, decade)
        return authors
        
    except Exception as e:
        logger.error(f"❌ Error fetching authors by decade: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch authors by decade"
        )

@router.get("/{author_id}", response_model=AuthorWithBooks)
async def get_author(
    author_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific author by ID, including their books and biographical information.
    
    **Public endpoint - no authentication required.**
    
    **Enhanced Features:**
    - Complete biographical information
    - Calculated age and years active
    - Associated books list
    """
    try:
        logger.info(f"🔍 Fetching author: {author_id}")
        author = AuthorService.get_author_by_id(db, author_id)
        
        if not author:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Author not found"
            )
        
        return author
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching author {author_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch author"
        )

@router.get("/{author_id}/biography", response_model=AuthorBiographical)
async def get_author_biography(
    author_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed biographical information for a specific author.
    
    **Public endpoint - no authentication required.**
    
    **Focus on:**
    - Biographical details only
    - Birth/death information
    - Education and achievements
    - No books list (for performance)
    """
    try:
        logger.info(f"📖 Fetching author biography: {author_id}")
        author = AuthorService.get_author_by_id(db, author_id)
        
        if not author:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Author not found"
            )
        
        return author
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching author biography {author_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch author biography"
        )

@router.put("/{author_id}", response_model=AuthorResponse)
async def update_author(
    author_id: int,
    author_data: AuthorUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)  # Only admins can update authors
):
    """
    Update an existing author with enhanced biographical information.
    
    **Admin access required.**
    
    **Enhanced Features:**
    - Update biographical details
    - Auto-populate year fields from date fields
    - Handle living status changes
    """
    try:
        logger.info(f"✏️ Updating author: {author_id}")
        author = AuthorService.update_author(db, author_id, author_data)
        return author
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error updating author {author_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update author"
        )

@router.put("/{author_id}/social-media")
async def update_author_social_media(
    author_id: int,
    social_media_data: Dict[str, str] = Body(..., 
        example={
            "twitter": "https://twitter.com/author",
            "instagram": "https://instagram.com/author",
            "facebook": "https://facebook.com/author",
            "linkedin": "https://linkedin.com/in/author"
        }
    ),
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)
):
    """
    Update an author's social media links.
    
    **Admin access required.**
    
    **Expected format:**
    ```json
    {
        "twitter": "https://twitter.com/username",
        "instagram": "https://instagram.com/username",
        "facebook": "https://facebook.com/username",
        "linkedin": "https://linkedin.com/in/username"
    }
    ```
    """
    try:
        logger.info(f"📱 Updating author social media: {author_id}")
        author = AuthorService.update_author_social_media(db, author_id, social_media_data)
        return {"message": "Social media links updated successfully", "author_id": author.id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error updating author social media {author_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update author social media"
        )

@router.delete("/{author_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_author(
    author_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_admin_user)  # Only admins can delete authors
):
    """
    Delete an author.
    
    **Admin access required.**
    
    Note: Cannot delete authors who have associated books.
    """
    try:
        logger.info(f"🗑️ Deleting author: {author_id}")
        AuthorService.delete_author(db, author_id)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error deleting author {author_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete author"
        )

@router.get("/search/suggestions", response_model=List[AuthorSummary])
async def get_author_suggestions(
    q: str = Query(..., min_length=2, description="Search query for author suggestions"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of suggestions"),
    db: Session = Depends(get_db)
):
    """
    Get author suggestions for autocomplete functionality.
    
    **Public endpoint - no authentication required.**
    
    **Enhanced Features:**
    - Search across multiple fields
    - Optimized for autocomplete UI
    """
    try:
        logger.info(f"🔍 Author suggestions for: {q}")
        authors = AuthorService.get_authors(db, limit=limit, search=q)
        return [AuthorSummary.from_orm(author) for author in authors]
        
    except Exception as e:
        logger.error(f"❌ Error getting author suggestions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get author suggestions"
        )
