"""
Database migration script to add Author model and update Book model
for many-to-many relationships.
"""

from sqlalchemy import create_engine, text
from app.config import settings
import logging

logger = logging.getLogger("BookLibraryAPI")

def migrate_database():
    """Run database migrations"""
    
    # Create database engine using the configured DATABASE_URL
    engine = create_engine(settings.DATABASE_URL, echo=True)
    
    with engine.connect() as connection:
        try:
            logger.info("🔄 Starting database migration...")
            
            # 1. Create authors table
            logger.info("📝 Creating authors table...")
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS authors (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    first_name VARCHAR(100) NOT NULL,
                    last_name VARCHAR(100) NOT NULL,
                    full_name VARCHAR(200) NOT NULL,
                    bio TEXT,
                    birth_year INT,
                    death_year INT,
                    nationality VARCHAR(100),
                    website VARCHAR(255),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_full_name (full_name)
                );
            """))
            
            # 2. Create book_authors association table
            logger.info("📝 Creating book_authors association table...")
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS book_authors (
                    book_id INT,
                    author_id INT,
                    PRIMARY KEY (book_id, author_id),
                    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
                    FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE CASCADE
                );
            """))
            
            # 3. Add new columns to books table
            logger.info("📝 Updating books table structure...")
            
            # Check if columns exist before adding them
            try:
                connection.execute(text("ALTER TABLE books ADD COLUMN isbn VARCHAR(20) UNIQUE;"))
                logger.info("✅ Added isbn column")
            except Exception:
                logger.info("ℹ️ isbn column already exists")
            
            try:
                connection.execute(text("ALTER TABLE books ADD COLUMN publisher VARCHAR(100);"))
                logger.info("✅ Added publisher column")
            except Exception:
                logger.info("ℹ️ publisher column already exists")
            
            try:
                connection.execute(text("ALTER TABLE books ADD COLUMN language VARCHAR(50) DEFAULT 'English';"))
                logger.info("✅ Added language column")
            except Exception:
                logger.info("ℹ️ language column already exists")
            
            try:
                connection.execute(text("ALTER TABLE books ADD COLUMN is_available TINYINT(1) DEFAULT 1;"))
                logger.info("✅ Added is_available column")
            except Exception:
                logger.info("ℹ️ is_available column already exists")
            
            try:
                connection.execute(text("ALTER TABLE books ADD COLUMN total_copies INT DEFAULT 1;"))
                logger.info("✅ Added total_copies column")
            except Exception:
                logger.info("ℹ️ total_copies column already exists")
            
            try:
                connection.execute(text("ALTER TABLE books ADD COLUMN available_copies INT DEFAULT 1;"))
                logger.info("✅ Added available_copies column")
            except Exception:
                logger.info("ℹ️ available_copies column already exists")
            
            # 4. Add index to title column
            try:
                connection.execute(text("ALTER TABLE books ADD INDEX idx_title (title);"))
                logger.info("✅ Added title index")
            except Exception:
                logger.info("ℹ️ Title index already exists")
            
            # 5. Migrate existing author data
            logger.info("📝 Migrating existing author data...")
            
            # Get all unique authors from the books table
            result = connection.execute(text("SELECT DISTINCT author FROM books WHERE author IS NOT NULL;"))
            existing_authors = result.fetchall()
            
            for (author_name,) in existing_authors:
                if author_name and author_name.strip():
                    # Split author name (simple approach - first word is first name, rest is last name)
                    name_parts = author_name.strip().split()
                    if len(name_parts) >= 2:
                        first_name = name_parts[0]
                        last_name = " ".join(name_parts[1:])
                    else:
                        first_name = author_name.strip()
                        last_name = "Unknown"
                    
                    # Insert author if not exists
                    connection.execute(text("""
                        INSERT IGNORE INTO authors (first_name, last_name, full_name)
                        VALUES (:first_name, :last_name, :full_name);
                    """), {
                        "first_name": first_name,
                        "last_name": last_name,
                        "full_name": author_name.strip()
                    })
            
            # 6. Create relationships between books and authors
            logger.info("📝 Creating book-author relationships...")
            
            # For each book, find its author and create the relationship
            books_result = connection.execute(text("SELECT id, author FROM books WHERE author IS NOT NULL;"))
            books = books_result.fetchall()
            
            for book_id, author_name in books:
                if author_name and author_name.strip():
                    # Find the author ID
                    author_result = connection.execute(text("""
                        SELECT id FROM authors WHERE full_name = :full_name LIMIT 1;
                    """), {"full_name": author_name.strip()})
                    
                    author_row = author_result.fetchone()
                    if author_row:
                        author_id = author_row[0]
                        
                        # Create the relationship
                        connection.execute(text("""
                            INSERT IGNORE INTO book_authors (book_id, author_id)
                            VALUES (:book_id, :author_id);
                        """), {
                            "book_id": book_id,
                            "author_id": author_id
                        })
            
            connection.commit()
            logger.info("✅ Database migration completed successfully!")
            
        except Exception as e:
            connection.rollback()
            logger.error(f"❌ Migration failed: {str(e)}")
            raise

if __name__ == "__main__":
    migrate_database()
