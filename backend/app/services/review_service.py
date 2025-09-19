from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from typing import List, Optional, Dict, Tuple
from datetime import datetime, timedelta
from app.models.review import BookReview, ReviewVote
from app.models.book import Book
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewVoteCreate
import logging

logger = logging.getLogger(__name__)

class ReviewService:
    """Service class for managing book reviews and ratings"""
    
    @staticmethod
    def create_review(db: Session, review_data: ReviewCreate, book_id: int, user_id: int) -> BookReview:
        """Create a new book review"""
        try:
            # Check if user already reviewed this book
            existing_review = db.query(BookReview).filter(
                BookReview.book_id == book_id,
                BookReview.user_id == user_id
            ).first()
            
            if existing_review:
                raise ValueError("User has already reviewed this book")
            
            # Verify book exists
            book = db.query(Book).filter(Book.id == book_id).first()
            if not book:
                raise ValueError("Book not found")
            
            # Create new review
            review = BookReview(
                **review_data.dict(),
                book_id=book_id,
                user_id=user_id
            )
            
            db.add(review)
            db.commit()
            db.refresh(review)
            
            logger.info(f"Review created: ID {review.id} for book {book_id} by user {user_id}")
            return review
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating review: {str(e)}")
            raise
    
    @staticmethod
    def get_review(db: Session, review_id: int) -> Optional[BookReview]:
        """Get review by ID"""
        return db.query(BookReview).filter(BookReview.id == review_id).first()
    
    @staticmethod
    def get_user_review_for_book(db: Session, book_id: int, user_id: int) -> Optional[BookReview]:
        """Get user's review for a specific book"""
        return db.query(BookReview).filter(
            BookReview.book_id == book_id,
            BookReview.user_id == user_id
        ).first()
    
    @staticmethod
    def update_review(db: Session, review_id: int, review_data: ReviewUpdate, user_id: int) -> Optional[BookReview]:
        """Update an existing review"""
        try:
            review = db.query(BookReview).filter(
                BookReview.id == review_id,
                BookReview.user_id == user_id
            ).first()
            
            if not review:
                return None
            
            # Update only provided fields
            update_data = review_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(review, field, value)
            
            review.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(review)
            
            logger.info(f"Review updated: ID {review_id}")
            return review
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating review: {str(e)}")
            raise
    
    @staticmethod
    def delete_review(db: Session, review_id: int, user_id: int) -> bool:
        """Delete a review"""
        try:
            review = db.query(BookReview).filter(
                BookReview.id == review_id,
                BookReview.user_id == user_id
            ).first()
            
            if not review:
                return False
            
            db.delete(review)
            db.commit()
            
            logger.info(f"Review deleted: ID {review_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting review: {str(e)}")
            raise
    
    @staticmethod
    def get_book_reviews(
        db: Session, 
        book_id: int, 
        skip: int = 0, 
        limit: int = 10,
        sort_by: str = "created_at",
        order: str = "desc",
        min_rating: Optional[int] = None,
        max_rating: Optional[int] = None,
        verified_only: bool = False
    ) -> Tuple[List[BookReview], int]:
        """Get reviews for a book with filtering and pagination"""
        
        query = db.query(BookReview).filter(BookReview.book_id == book_id)
        
        # Apply filters
        if min_rating is not None:
            query = query.filter(BookReview.rating >= min_rating)
        if max_rating is not None:
            query = query.filter(BookReview.rating <= max_rating)
        if verified_only:
            query = query.filter(BookReview.is_verified_purchase == True)
        
        # Get total count before applying pagination
        total = query.count()
        
        # Apply sorting
        if sort_by == "rating":
            order_field = BookReview.rating
        elif sort_by == "helpful_votes":
            order_field = BookReview.helpful_votes
        elif sort_by == "helpfulness_ratio":
            order_field = func.coalesce(
                func.nullif(BookReview.helpful_votes, 0) / func.nullif(BookReview.total_votes, 0), 
                0
            )
        else:  # default to created_at
            order_field = BookReview.created_at
        
        if order.lower() == "desc":
            query = query.order_by(desc(order_field))
        else:
            query = query.order_by(order_field)
        
        # Apply pagination
        reviews = query.offset(skip).limit(limit).all()
        
        return reviews, total
    
    @staticmethod
    def get_user_reviews(
        db: Session, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 10
    ) -> Tuple[List[BookReview], int]:
        """Get all reviews by a user"""
        
        query = db.query(BookReview).filter(BookReview.user_id == user_id)
        total = query.count()
        
        reviews = query.order_by(desc(BookReview.created_at)).offset(skip).limit(limit).all()
        
        return reviews, total
    
    @staticmethod
    def vote_on_review(db: Session, review_id: int, user_id: int, vote_data: ReviewVoteCreate) -> ReviewVote:
        """Vote on review helpfulness"""
        try:
            # Check if user already voted on this review
            existing_vote = db.query(ReviewVote).filter(
                ReviewVote.review_id == review_id,
                ReviewVote.user_id == user_id
            ).first()
            
            if existing_vote:
                # Update existing vote
                existing_vote.is_helpful = vote_data.is_helpful
                existing_vote.created_at = datetime.utcnow()
                vote = existing_vote
            else:
                # Create new vote
                vote = ReviewVote(
                    review_id=review_id,
                    user_id=user_id,
                    is_helpful=vote_data.is_helpful
                )
                db.add(vote)
            
            db.commit()
            
            # Update review helpfulness counters
            ReviewService._update_review_helpfulness(db, review_id)
            
            logger.info(f"Vote recorded for review {review_id} by user {user_id}")
            return vote
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error voting on review: {str(e)}")
            raise
    
    @staticmethod
    def _update_review_helpfulness(db: Session, review_id: int):
        """Update review helpfulness counters"""
        try:
            helpful_count = db.query(func.count(ReviewVote.id)).filter(
                ReviewVote.review_id == review_id,
                ReviewVote.is_helpful == True
            ).scalar() or 0
            
            total_votes = db.query(func.count(ReviewVote.id)).filter(
                ReviewVote.review_id == review_id
            ).scalar() or 0
            
            review = db.query(BookReview).filter(BookReview.id == review_id).first()
            if review:
                review.helpful_votes = helpful_count
                review.total_votes = total_votes
                db.commit()
                
        except Exception as e:
            logger.error(f"Error updating review helpfulness: {str(e)}")
            raise
    
    @staticmethod
    def get_review_stats(db: Session, book_id: int) -> Dict:
        """Get comprehensive review statistics for a book"""
        try:
            # Basic stats
            stats = db.query(
                func.count(BookReview.id).label('total_reviews'),
                func.avg(BookReview.rating).label('average_rating'),
                func.count(func.nullif(BookReview.is_verified_purchase, False)).label('verified_reviews')
            ).filter(BookReview.book_id == book_id).first()
            
            # Rating distribution
            rating_dist = db.query(
                BookReview.rating,
                func.count(BookReview.id).label('count')
            ).filter(BookReview.book_id == book_id).group_by(BookReview.rating).all()
            
            rating_distribution = {i: 0 for i in range(1, 6)}
            for rating, count in rating_dist:
                rating_distribution[rating] = count
            
            # Helpful reviews count
            helpful_reviews = db.query(func.count(BookReview.id)).filter(
                BookReview.book_id == book_id,
                BookReview.helpful_votes > 0
            ).scalar() or 0
            
            return {
                'total_reviews': stats.total_reviews or 0,
                'average_rating': round(float(stats.average_rating or 0), 2),
                'rating_distribution': rating_distribution,
                'helpful_reviews_count': helpful_reviews,
                'verified_reviews_count': stats.verified_reviews or 0
            }
            
        except Exception as e:
            logger.error(f"Error getting review stats: {str(e)}")
            return {
                'total_reviews': 0,
                'average_rating': 0.0,
                'rating_distribution': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
                'helpful_reviews_count': 0,
                'verified_reviews_count': 0
            }
    
    @staticmethod
    def get_trending_reviews(db: Session, days: int = 7, limit: int = 10) -> List[BookReview]:
        """Get trending/most helpful reviews from recent period"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        reviews = db.query(BookReview).filter(
            BookReview.created_at >= cutoff_date,
            BookReview.helpful_votes > 0
        ).order_by(
            desc(BookReview.helpful_votes),
            desc(BookReview.created_at)
        ).limit(limit).all()
        
        return reviews
    
    @staticmethod
    def search_reviews(
        db: Session, 
        query: str, 
        skip: int = 0, 
        limit: int = 10
    ) -> Tuple[List[BookReview], int]:
        """Search reviews by text content"""
        
        search_query = db.query(BookReview).filter(
            or_(
                BookReview.title.ilike(f"%{query}%"),
                BookReview.review_text.ilike(f"%{query}%")
            )
        )
        
        total = search_query.count()
        reviews = search_query.order_by(desc(BookReview.created_at)).offset(skip).limit(limit).all()
        
        return reviews, total
    
    @staticmethod
    def get_review_analytics(db: Session, days: int = 30) -> Dict:
        """Get comprehensive review analytics"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Basic analytics
            total_reviews = db.query(func.count(BookReview.id)).scalar() or 0
            avg_rating = db.query(func.avg(BookReview.rating)).scalar() or 0
            
            # Recent reviews
            recent_reviews = db.query(func.count(BookReview.id)).filter(
                BookReview.created_at >= cutoff_date
            ).scalar() or 0
            
            # Rating distribution
            rating_dist = db.query(
                BookReview.rating,
                func.count(BookReview.id).label('count')
            ).group_by(BookReview.rating).all()
            
            rating_distribution = {str(i): 0 for i in range(1, 6)}
            for rating, count in rating_dist:
                rating_distribution[str(rating)] = count
            
            # Top reviewers (users with most reviews)
            top_reviewers = db.query(
                User.username,
                User.first_name,
                User.last_name,
                func.count(BookReview.id).label('review_count'),
                func.avg(BookReview.rating).label('avg_rating')
            ).join(BookReview).group_by(User.id).order_by(
                desc(func.count(BookReview.id))
            ).limit(5).all()
            
            top_reviewers_list = [
                {
                    'username': reviewer.username,
                    'name': f"{reviewer.first_name or ''} {reviewer.last_name or ''}".strip(),
                    'review_count': reviewer.review_count,
                    'average_rating': round(float(reviewer.avg_rating), 2)
                }
                for reviewer in top_reviewers
            ]
            
            return {
                'total_reviews': total_reviews,
                'average_rating': round(float(avg_rating), 2),
                'rating_distribution': rating_distribution,
                'reviews_this_month': recent_reviews,
                'top_reviewers': top_reviewers_list
            }
            
        except Exception as e:
            logger.error(f"Error getting review analytics: {str(e)}")
            return {
                'total_reviews': 0,
                'average_rating': 0.0,
                'rating_distribution': {str(i): 0 for i in range(1, 6)},
                'reviews_this_month': 0,
                'top_reviewers': []
            }
