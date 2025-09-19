#!/usr/bin/env python3
import sys
import os
sys.path.append('/Users/aditya_takawale/Book_library_api_2/backend')

from app.database import SessionLocal
from app.models.book import Book
from app.models.user import User

def test_database():
    db = SessionLocal()
    try:
        print("Testing database connection...")
        
        # Test users table
        user_count = db.query(User).count()
        print(f"Users in database: {user_count}")
        
        # Test books table
        try:
            book_count = db.query(Book).count()
            print(f"Books in database: {book_count}")
            
            # Get first few books
            books = db.query(Book).limit(3).all()
            print(f"First 3 books:")
            for book in books:
                print(f"  - {book.title} (ID: {book.id})")
                
        except Exception as e:
            print(f"Error querying books: {e}")
            
    except Exception as e:
        print(f"Database connection error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_database()
