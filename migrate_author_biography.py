#!/usr/bin/env python3
"""
Database Migration Script: Enhanced Author Biography
====================================================

This script adds new biographical fields to the existing authors table
to support comprehensive author profile management.

New fields added:
- birth_date (DATE) - Full birth date
- death_date (DATE) - Full death date
- birth_place (VARCHAR(200)) - Birth location
- education (TEXT) - Educational background
- awards (TEXT) - Literary awards and honors
- genres (VARCHAR(500)) - Primary writing genres
- wikipedia_url (VARCHAR(255)) - Wikipedia page link
- social_media (TEXT) - Social media links (JSON)
- is_living (INTEGER) - Living status (1=living, 0=deceased)

Usage:
    python migrate_author_biography.py
"""

import sys
import os
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent / "app"))

from sqlalchemy import create_engine, text, MetaData, Table, Column, String, Text, Date, Integer
from sqlalchemy.exc import OperationalError
from app.config import settings
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_database_engine():
    """Create database engine"""
    try:
        DATABASE_URL = settings.DATABASE_URL
        engine = create_engine(DATABASE_URL, echo=False)
        return engine
    except Exception as e:
        logger.error(f"Failed to create database engine: {e}")
        sys.exit(1)

def check_column_exists(engine, table_name, column_name):
    """Check if a column exists in a table"""
    try:
        # Extract database name from DATABASE_URL
        db_name = "library_db"  # Default database name
        if "library_db" in settings.DATABASE_URL:
            db_name = "library_db"
        
        with engine.connect() as connection:
            result = connection.execute(text(f"""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = '{db_name}' 
                AND TABLE_NAME = '{table_name}' 
                AND COLUMN_NAME = '{column_name}'
            """))
            return result.scalar() > 0
    except Exception as e:
        logger.error(f"Error checking column {column_name}: {e}")
        return False

def add_column_if_not_exists(engine, table_name, column_name, column_definition):
    """Add a column to a table if it doesn't exist"""
    try:
        if not check_column_exists(engine, table_name, column_name):
            sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"
            with engine.connect() as connection:
                connection.execute(text(sql))
                connection.commit()
            logger.info(f"✅ Added column '{column_name}' to table '{table_name}'")
            return True
        else:
            logger.info(f"ℹ️  Column '{column_name}' already exists in table '{table_name}'")
            return False
    except Exception as e:
        logger.error(f"❌ Error adding column '{column_name}': {e}")
        return False

def migrate_author_biography():
    """Run the author biography migration"""
    logger.info("🚀 Starting Author Biography Migration")
    logger.info("=" * 50)
    
    engine = get_database_engine()
    
    try:
        # Test database connection
        with engine.connect() as connection:
            logger.info("✅ Database connection successful")
        
        # Define new columns to add
        new_columns = [
            ("birth_date", "DATE NULL"),
            ("death_date", "DATE NULL"),
            ("birth_place", "VARCHAR(200) NULL"),
            ("education", "TEXT NULL"),
            ("awards", "TEXT NULL"),
            ("genres", "VARCHAR(500) NULL"),
            ("wikipedia_url", "VARCHAR(255) NULL"),
            ("social_media", "TEXT NULL"),
            ("is_living", "INTEGER DEFAULT 1")
        ]
        
        logger.info("📝 Adding new biographical columns to authors table:")
        
        # Add each column
        columns_added = 0
        for column_name, column_definition in new_columns:
            if add_column_if_not_exists(engine, "authors", column_name, column_definition):
                columns_added += 1
        
        # Update existing data to populate is_living field based on death_year
        if columns_added > 0:
            logger.info("🔄 Updating existing author data...")
            
            # Set is_living = 0 for authors with death_year
            with engine.connect() as connection:
                result = connection.execute(text("""
                    UPDATE authors 
                    SET is_living = 0 
                    WHERE death_year IS NOT NULL AND is_living = 1
                """))
                connection.commit()
                deceased_count = result.rowcount
            
            if deceased_count > 0:
                logger.info(f"✅ Updated {deceased_count} authors to deceased status")
            
            # Get total author count
            with engine.connect() as connection:
                result = connection.execute(text("SELECT COUNT(*) FROM authors"))
                total_authors = result.scalar()
            
            logger.info(f"📊 Migration Summary:")
            logger.info(f"   • Total authors: {total_authors}")
            logger.info(f"   • New columns added: {columns_added}")
            logger.info(f"   • Authors marked as deceased: {deceased_count}")
            logger.info(f"   • Living authors: {total_authors - deceased_count}")
        
        logger.info("✅ Author Biography Migration completed successfully!")
        
        # Show sample of enhanced author data
        logger.info("\n📋 Sample of author data with new fields:")
        logger.info("-" * 60)
        
        with engine.connect() as connection:
            result = connection.execute(text("""
                SELECT id, full_name, nationality, birth_year, death_year, is_living 
                FROM authors 
                LIMIT 5
            """))
            
            for row in result:
                status = "Living" if row[5] == 1 else "Deceased"
                logger.info(f"   {row[0]:2d}. {row[1]:<25} | {row[2] or 'Unknown':<15} | {row[3] or 'Unknown'}-{row[4] or 'Present':<6} | {status}")
        
        logger.info("\n🎉 Enhanced Author Management is now ready!")
        logger.info("New features available:")
        logger.info("• Full birth/death dates")
        logger.info("• Birth place tracking")
        logger.info("• Educational background")
        logger.info("• Awards and honors")
        logger.info("• Writing genres")
        logger.info("• Social media links")
        logger.info("• Living status tracking")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        sys.exit(1)
    finally:
        engine.dispose()

if __name__ == "__main__":
    migrate_author_biography()
