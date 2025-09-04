from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.db import get_db
from app.utils.dependencies import get_current_user
from app.models.user import User
from app.services.review_service import ReviewService
from app.schemas.review import (
    ReviewCreate, ReviewUpdate, ReviewResponse, ReviewSummary, 
    ReviewWithBook, ReviewStats, BookWithReviews, ReviewVoteCreate, 
    ReviewVoteResponse, ReviewAnalytics
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reviews", tags=["reviews"])

@router.post("/books/{book_id}", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    book_id: int,
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new review for a book"""
    try:
        review = ReviewService.create_review(
            db=db, 
            review_data=review_data, 
            book_id=book_id, 
            user_id=current_user.id
        )
        return review
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating review: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{review_id}", response_model=ReviewResponse)
async def get_review(
    review_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific review by ID"""
    review = ReviewService.get_review(db=db, review_id=review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review

@router.put("/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: int,
    review_data: ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a review (only by the review author)"""
    try:
        review = ReviewService.update_review(
            db=db, 
            review_id=review_id, 
            review_data=review_data, 
            user_id=current_user.id
        )
        if not review:
            raise HTTPException(status_code=404, detail="Review not found or unauthorized")
        return review
    except Exception as e:
        logger.error(f"Error updating review: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a review (only by the review author or admin)"""
    try:
        # Allow admins to delete any review
        if current_user.role == "Admin":
            review = ReviewService.get_review(db=db, review_id=review_id)
            if not review:
                raise HTTPException(status_code=404, detail="Review not found")
            ReviewService.delete_review(db=db, review_id=review_id, user_id=review.user_id)
        else:
            success = ReviewService.delete_review(
                db=db, 
                review_id=review_id, 
                user_id=current_user.id
            )
            if not success:
                raise HTTPException(status_code=404, detail="Review not found or unauthorized")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting review: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/books/{book_id}/reviews", response_model=dict)
async def get_book_reviews(
    book_id: int,
    skip: int = Query(0, ge=0, description="Number of reviews to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of reviews to return"),
    sort_by: str = Query("created_at", regex="^(created_at|rating|helpful_votes|helpfulness_ratio)$"),
    order: str = Query("desc", regex="^(asc|desc)$"),
    min_rating: Optional[int] = Query(None, ge=1, le=5),
    max_rating: Optional[int] = Query(None, ge=1, le=5),
    verified_only: bool = Query(False, description="Show only verified purchase reviews"),
    db: Session = Depends(get_db)
):
    """Get reviews for a specific book with filtering and pagination"""
    try:
        reviews, total = ReviewService.get_book_reviews(
            db=db,
            book_id=book_id,
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            order=order,
            min_rating=min_rating,
            max_rating=max_rating,
            verified_only=verified_only
        )
        
        return {
            "reviews": reviews,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": skip + limit < total
        }
    except Exception as e:
        logger.error(f"Error getting book reviews: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/books/{book_id}/stats", response_model=ReviewStats)
async def get_book_review_stats(
    book_id: int,
    db: Session = Depends(get_db)
):
    """Get review statistics for a book"""
    try:
        stats = ReviewService.get_review_stats(db=db, book_id=book_id)
        return stats
    except Exception as e:
        logger.error(f"Error getting review stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/users/{user_id}/reviews", response_model=dict)
async def get_user_reviews(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all reviews by a specific user"""
    try:
        reviews, total = ReviewService.get_user_reviews(
            db=db,
            user_id=user_id,
            skip=skip,
            limit=limit
        )
        
        return {
            "reviews": reviews,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": skip + limit < total
        }
    except Exception as e:
        logger.error(f"Error getting user reviews: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/me/reviews", response_model=dict)
async def get_my_reviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's reviews"""
    try:
        reviews, total = ReviewService.get_user_reviews(
            db=db,
            user_id=current_user.id,
            skip=skip,
            limit=limit
        )
        
        return {
            "reviews": reviews,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": skip + limit < total
        }
    except Exception as e:
        logger.error(f"Error getting user reviews: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/books/{book_id}/my-review", response_model=ReviewResponse)
async def get_my_review_for_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's review for a specific book"""
    review = ReviewService.get_user_review_for_book(
        db=db, 
        book_id=book_id, 
        user_id=current_user.id
    )
    if not review:
        raise HTTPException(status_code=404, detail="No review found for this book")
    return review

@router.post("/{review_id}/vote", response_model=ReviewVoteResponse, status_code=status.HTTP_201_CREATED)
async def vote_on_review(
    review_id: int,
    vote_data: ReviewVoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Vote on review helpfulness"""
    try:
        # Prevent users from voting on their own reviews
        review = ReviewService.get_review(db=db, review_id=review_id)
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
        
        if review.user_id == current_user.id:
            raise HTTPException(status_code=400, detail="Cannot vote on your own review")
        
        vote = ReviewService.vote_on_review(
            db=db,
            review_id=review_id,
            user_id=current_user.id,
            vote_data=vote_data
        )
        return vote
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error voting on review: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/trending", response_model=List[ReviewSummary])
async def get_trending_reviews(
    days: int = Query(7, ge=1, le=90, description="Number of days to look back"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get trending/most helpful reviews from recent period"""
    try:
        reviews = ReviewService.get_trending_reviews(db=db, days=days, limit=limit)
        return reviews
    except Exception as e:
        logger.error(f"Error getting trending reviews: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/search", response_model=dict)
async def search_reviews(
    q: str = Query(..., min_length=3, description="Search query"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Search reviews by text content"""
    try:
        reviews, total = ReviewService.search_reviews(
            db=db,
            query=q,
            skip=skip,
            limit=limit
        )
        
        return {
            "reviews": reviews,
            "total": total,
            "query": q,
            "skip": skip,
            "limit": limit,
            "has_more": skip + limit < total
        }
    except Exception as e:
        logger.error(f"Error searching reviews: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/analytics", response_model=ReviewAnalytics)
async def get_review_analytics(
    days: int = Query(30, ge=1, le=365, description="Number of days for analytics"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive review analytics (Admin only)"""
    if current_user.role != "Admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        analytics = ReviewService.get_review_analytics(db=db, days=days)
        return analytics
    except Exception as e:
        logger.error(f"Error getting review analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
