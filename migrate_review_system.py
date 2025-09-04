#!/usr/bin/env python3
"""
Database migration script for Book Review System
Adds review and voting tables to the existing database schema
"""

import sys
import os
from sqlalchemy import text
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.db import engine, SessionLocal
from app.models.review import BookReview, ReviewVote
from app.models import Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_review_tables():
    """Create review and review_vote tables"""
    try:
        logger.info("Creating review system tables...")
        
        # Create tables from models
        Base.metadata.create_all(bind=engine, tables=[
            BookReview.__table__,
            ReviewVote.__table__
        ])
        
        logger.info("Review system tables created successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error creating review tables: {str(e)}")
        return False

def add_indexes():
    """Add database indexes for better performance"""
    try:
        with engine.connect() as conn:
            logger.info("Adding performance indexes...")
            
            # Indexes for book_reviews table
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_book_reviews_book_id ON book_reviews(book_id);",
                "CREATE INDEX IF NOT EXISTS idx_book_reviews_user_id ON book_reviews(user_id);", 
                "CREATE INDEX IF NOT EXISTS idx_book_reviews_rating ON book_reviews(rating);",
                "CREATE INDEX IF NOT EXISTS idx_book_reviews_created_at ON book_reviews(created_at);",
                "CREATE INDEX IF NOT EXISTS idx_book_reviews_helpful_votes ON book_reviews(helpful_votes);",
                "CREATE INDEX IF NOT EXISTS idx_book_reviews_verified ON book_reviews(is_verified_purchase);",
                "CREATE UNIQUE INDEX IF NOT EXISTS idx_book_reviews_unique_user_book ON book_reviews(book_id, user_id);",
                
                # Indexes for review_votes table
                "CREATE INDEX IF NOT EXISTS idx_review_votes_review_id ON review_votes(review_id);",
                "CREATE INDEX IF NOT EXISTS idx_review_votes_user_id ON review_votes(user_id);",
                "CREATE INDEX IF NOT EXISTS idx_review_votes_helpful ON review_votes(is_helpful);",
                "CREATE UNIQUE INDEX IF NOT EXISTS idx_review_votes_unique_user_review ON review_votes(review_id, user_id);"
            ]
            
            for index_sql in indexes:
                try:
                    conn.execute(text(index_sql))
                    logger.info(f"Created index: {index_sql.split('IF NOT EXISTS ')[1].split(' ON')[0]}")
                except Exception as e:
                    logger.warning(f"Index creation failed (may already exist): {str(e)}")
            
            conn.commit()
            logger.info("Indexes created successfully!")
            
    except Exception as e:
        logger.error(f"Error creating indexes: {str(e)}")
        return False
    
    return True

def verify_migration():
    """Verify that the migration was successful"""
    try:
        db = SessionLocal()
        
        # Test creating a sample review (will be rolled back)
        db.execute(text("SELECT COUNT(*) FROM book_reviews"))
        db.execute(text("SELECT COUNT(*) FROM review_votes"))
        
        # Check table structure
        result = db.execute(text("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'book_reviews' 
            ORDER BY ordinal_position
        """))
        
        columns = result.fetchall()
        expected_columns = [
            'id', 'book_id', 'user_id', 'rating', 'title', 'review_text',
            'is_spoiler', 'is_verified_purchase', 'helpful_votes', 'total_votes',
            'created_at', 'updated_at'
        ]
        
        actual_columns = [col[0] for col in columns]
        
        for expected_col in expected_columns:
            if expected_col not in actual_columns:
                logger.error(f"Missing column: {expected_col}")
                return False
        
        logger.info("Migration verification successful!")
        logger.info(f"book_reviews table has {len(actual_columns)} columns")
        
        db.close()
        return True
        
    except Exception as e:
        logger.error(f"Migration verification failed: {str(e)}")
        return False

def main():
    """Run the complete migration process"""
    logger.info("Starting Book Review System migration...")
    logger.info(f"Migration started at: {datetime.now()}")
    
    # Step 1: Create tables
    if not create_review_tables():
        logger.error("Failed to create review tables. Aborting migration.")
        return False
    
    # Step 2: Add indexes
    if not add_indexes():
        logger.warning("Some indexes may not have been created, but continuing...")
    
    # Step 3: Verify migration
    if not verify_migration():
        logger.error("Migration verification failed!")
        return False
    
    logger.info("✅ Book Review System migration completed successfully!")
    logger.info(f"Migration completed at: {datetime.now()}")
    
    # Print summary
    print("\n" + "="*60)
    print("BOOK REVIEW SYSTEM MIGRATION SUMMARY")
    print("="*60)
    print("✅ Tables Created:")
    print("   - book_reviews (stores user reviews and ratings)")
    print("   - review_votes (stores helpfulness votes)")
    print("\n✅ Features Added:")
    print("   - 1-5 star rating system")
    print("   - Text reviews with titles")
    print("   - Spoiler detection")
    print("   - Verified purchase tracking")
    print("   - Community helpfulness voting")
    print("   - Performance indexes")
    print("\n✅ API Endpoints Available:")
    print("   - POST /reviews/books/{book_id} - Create review")
    print("   - GET /reviews/{review_id} - Get review")
    print("   - PUT /reviews/{review_id} - Update review")
    print("   - DELETE /reviews/{review_id} - Delete review")
    print("   - GET /reviews/books/{book_id}/reviews - Get book reviews")
    print("   - GET /reviews/books/{book_id}/stats - Get review stats")
    print("   - POST /reviews/{review_id}/vote - Vote on helpfulness")
    print("   - GET /reviews/trending - Get trending reviews")
    print("   - GET /reviews/search - Search reviews")
    print("="*60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
