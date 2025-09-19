"""
Service layer for book loan and reservation management.
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal

from app.models.loan import BookLoan, BookReservation, LoanStatus, ReservationStatus
from app.models.book import Book
from app.models.user import User
from app.schemas.loan import (
    BookLoanCreate, BookLoanUpdate, BookLoanResponse,
    BookReservationCreate, BookReservationUpdate, BookReservationResponse,
    LoanStatistics, ReservationStatistics, BookAvailabilityInfo
)
import logging

logger = logging.getLogger("LoanService")

class LoanService:
    """Service for managing book loans."""
    
    @staticmethod
    def create_loan(db: Session, loan_data: dict, user_id: int) -> BookLoan:
        """Create a new book loan."""
        book_id = loan_data.get("book_id")
        # Check book availability
        book = db.query(Book).filter(Book.id == book_id).first()
        if not book:
            raise ValueError("Book not found")
        
        if book.available_copies <= 0:
            raise ValueError("No copies available for loan")
        
        # Check if user already has an active loan for this book
        existing_loan = db.query(BookLoan).filter(
            and_(
                BookLoan.book_id == book_id,
                BookLoan.user_id == user_id,
                BookLoan.status.in_([LoanStatus.ACTIVE, LoanStatus.RENEWED])
            )
        ).first()
        
        if existing_loan:
            raise ValueError("User already has an active loan for this book")
        
        # Create loan
        loan = BookLoan(
            book_id=book_id,
            user_id=user_id,
            due_date=loan_data.get("due_date"),
            notes=loan_data.get("notes"),
            status=LoanStatus.ACTIVE
        )
        
        # Update book availability
        book.available_copies -= 1
        book.update_popularity_score()
        
        db.add(loan)
        db.commit()
        db.refresh(loan)
        
        logger.info(f"Loan created: Book {book_id} to User {user_id}")
        return loan
    
    @staticmethod
    def return_book(db: Session, loan_id: int, librarian_id: int) -> BookLoan:
        """Process book return."""
        loan = db.query(BookLoan).filter(BookLoan.id == loan_id).first()
        if not loan:
            raise ValueError("Loan not found")
        
        if loan.status == LoanStatus.RETURNED:
            raise ValueError("Book already returned")
        
        # Update loan
        loan.return_date = datetime.now()
        loan.status = LoanStatus.RETURNED
        
        # Calculate fine if overdue
        if datetime.now() > loan.due_date:
            days_overdue = (datetime.now() - loan.due_date).days
            loan.fine_amount = Decimal(str(days_overdue * 1.00))  # $1 per day
        
        # Update book availability
        book = db.query(Book).filter(Book.id == loan.book_id).first()
        if book:
            book.available_copies += 1
        
        # Check for reservations and fulfill next in queue
        LoanService._fulfill_next_reservation(db, loan.book_id)
        
        db.commit()
        db.refresh(loan)
        
        logger.info(f"Book returned: Loan {loan_id}")
        return loan
    
    @staticmethod
    def renew_loan(db: Session, loan_id: int, extension_days: int = 14) -> BookLoan:
        """Renew a book loan."""
        loan = db.query(BookLoan).filter(BookLoan.id == loan_id).first()
        if not loan:
            raise ValueError("Loan not found")
        
        if loan.status != LoanStatus.ACTIVE:
            raise ValueError("Only active loans can be renewed")
        
        if loan.renewal_count >= 2:  # Max 2 renewals
            raise ValueError("Maximum renewal limit reached")
        
        # Check if there are pending reservations
        pending_reservations = db.query(BookReservation).filter(
            and_(
                BookReservation.book_id == loan.book_id,
                BookReservation.status == ReservationStatus.PENDING
            )
        ).count()
        
        if pending_reservations > 0:
            raise ValueError("Cannot renew: Book has pending reservations")
        
        # Renew loan
        loan.due_date = loan.due_date + timedelta(days=extension_days)
        loan.renewal_count += 1
        loan.status = LoanStatus.RENEWED
        
        db.commit()
        db.refresh(loan)
        
        logger.info(f"Loan renewed: {loan_id} for {extension_days} days")
        return loan
    
    @staticmethod
    def get_user_loans(db: Session, user_id: int, status: Optional[LoanStatus] = None) -> List[BookLoan]:
        """Get loans for a specific user."""
        query = db.query(BookLoan).filter(BookLoan.user_id == user_id)
        
        if status:
            query = query.filter(BookLoan.status == status)
        
        return query.order_by(desc(BookLoan.loan_date)).all()
    
    @staticmethod
    def get_overdue_loans(db: Session) -> List[BookLoan]:
        """Get all overdue loans."""
        return db.query(BookLoan).filter(
            and_(
                BookLoan.status.in_([LoanStatus.ACTIVE, LoanStatus.RENEWED]),
                BookLoan.due_date < datetime.now()
            )
        ).all()
    
    @staticmethod
    def get_all_loans(db: Session, skip: int = 0, limit: int = 10, status: Optional[LoanStatus] = None, search: Optional[str] = None) -> tuple[int, List[BookLoan]]:
        """Get all loans with pagination, filtering, and searching."""
        query = db.query(BookLoan).join(Book, BookLoan.book_id == Book.id).join(User, BookLoan.user_id == User.id)
        
        if status:
            query = query.filter(BookLoan.status == status)
        
        if search:
            search_term = f"%{search.lower()}%"
            query = query.filter(
                or_(
                    User.username.ilike(search_term),
                    User.email.ilike(search_term),
                    Book.title.ilike(search_term),
                    Book.isbn.ilike(search_term)
                )
            )
            
        total = query.count()
        loans = query.order_by(desc(BookLoan.loan_date)).offset(skip).limit(limit).all()
        
        return total, loans
    
    @staticmethod
    def update_overdue_status(db: Session) -> int:
        """Update status of overdue loans."""
        overdue_loans = LoanService.get_overdue_loans(db)
        
        for loan in overdue_loans:
            loan.status = LoanStatus.OVERDUE
            # Calculate fine
            days_overdue = (datetime.now() - loan.due_date).days
            loan.fine_amount = Decimal(str(days_overdue * 1.00))  # $1 per day
        
        db.commit()
        logger.info(f"Updated {len(overdue_loans)} loans to overdue status")
        return len(overdue_loans)
    
    @staticmethod
    def get_loan_statistics(db: Session) -> LoanStatistics:
        """Get loan statistics."""
        total_loans = db.query(BookLoan).count()
        active_loans = db.query(BookLoan).filter(BookLoan.status == LoanStatus.ACTIVE).count()
        overdue_loans = db.query(BookLoan).filter(BookLoan.status == LoanStatus.OVERDUE).count()
        returned_loans = db.query(BookLoan).filter(BookLoan.status == LoanStatus.RETURNED).count()
        
        total_fines = db.query(BookLoan).filter(BookLoan.fine_amount > 0).with_entities(
            db.func.sum(BookLoan.fine_amount)
        ).scalar() or Decimal('0.00')
        
        return LoanStatistics(
            total_loans=total_loans,
            active_loans=active_loans,
            overdue_loans=overdue_loans,
            returned_loans=returned_loans,
            total_fine_amount=total_fines
        )
    
    @staticmethod
    def _fulfill_next_reservation(db: Session, book_id: int) -> Optional[BookReservation]:
        """Fulfill the next reservation in queue when a book becomes available."""
        reservation = db.query(BookReservation).filter(
            and_(
                BookReservation.book_id == book_id,
                BookReservation.status == ReservationStatus.PENDING
            )
        ).order_by(asc(BookReservation.priority), asc(BookReservation.reservation_date)).first()
        
        if reservation:
            reservation.status = ReservationStatus.FULFILLED
            reservation.notification_sent = True
            db.commit()
            
            logger.info(f"Reservation fulfilled: {reservation.id}")
            return reservation
        
        return None

class ReservationService:
    """Service for managing book reservations."""
    
    @staticmethod
    def create_reservation(db: Session, reservation_data: BookReservationCreate) -> BookReservation:
        """Create a new book reservation."""
        # Check if book exists
        book = db.query(Book).filter(Book.id == reservation_data.book_id).first()
        if not book:
            raise ValueError("Book not found")
        
        # Check if user already has a reservation for this book
        existing_reservation = db.query(BookReservation).filter(
            and_(
                BookReservation.book_id == reservation_data.book_id,
                BookReservation.user_id == reservation_data.user_id,
                BookReservation.status == ReservationStatus.PENDING
            )
        ).first()
        
        if existing_reservation:
            raise ValueError("User already has a pending reservation for this book")
        
        # Check if user already has an active loan for this book
        active_loan = db.query(BookLoan).filter(
            and_(
                BookLoan.book_id == reservation_data.book_id,
                BookLoan.user_id == reservation_data.user_id,
                BookLoan.status.in_([LoanStatus.ACTIVE, LoanStatus.RENEWED])
            )
        ).first()
        
        if active_loan:
            raise ValueError("User already has this book on loan")
        
        # Create reservation
        reservation = BookReservation(
            book_id=reservation_data.book_id,
            user_id=reservation_data.user_id,
            expiry_date=reservation_data.expiry_date,
            priority=reservation_data.priority,
            notes=reservation_data.notes,
            status=ReservationStatus.PENDING
        )
        
        # Update book reserved copies
        book.reserved_copies += 1
        
        db.add(reservation)
        db.commit()
        db.refresh(reservation)
        
        logger.info(f"Reservation created: Book {reservation_data.book_id} for User {reservation_data.user_id}")
        return reservation
    
    @staticmethod
    def cancel_reservation(db: Session, reservation_id: int, user_id: Optional[int] = None) -> BookReservation:
        """Cancel a reservation."""
        query = db.query(BookReservation).filter(BookReservation.id == reservation_id)
        
        if user_id:
            query = query.filter(BookReservation.user_id == user_id)
        
        reservation = query.first()
        if not reservation:
            raise ValueError("Reservation not found")
        
        if reservation.status != ReservationStatus.PENDING:
            raise ValueError("Only pending reservations can be cancelled")
        
        # Update reservation
        reservation.status = ReservationStatus.CANCELLED
        
        # Update book reserved copies
        book = db.query(Book).filter(Book.id == reservation.book_id).first()
        if book and book.reserved_copies > 0:
            book.reserved_copies -= 1
        
        db.commit()
        db.refresh(reservation)
        
        logger.info(f"Reservation cancelled: {reservation_id}")
        return reservation
    
    @staticmethod
    def get_user_reservations(db: Session, user_id: int, status: Optional[ReservationStatus] = None) -> List[BookReservation]:
        """Get reservations for a specific user."""
        query = db.query(BookReservation).filter(BookReservation.user_id == user_id)
        
        if status:
            query = query.filter(BookReservation.status == status)
        
        return query.order_by(desc(BookReservation.reservation_date)).all()
    
    @staticmethod
    def expire_old_reservations(db: Session) -> int:
        """Expire old reservations."""
        expired_reservations = db.query(BookReservation).filter(
            and_(
                BookReservation.status == ReservationStatus.PENDING,
                BookReservation.expiry_date < datetime.now()
            )
        ).all()
        
        for reservation in expired_reservations:
            reservation.status = ReservationStatus.EXPIRED
            
            # Update book reserved copies
            book = db.query(Book).filter(Book.id == reservation.book_id).first()
            if book and book.reserved_copies > 0:
                book.reserved_copies -= 1
        
        db.commit()
        logger.info(f"Expired {len(expired_reservations)} reservations")
        return len(expired_reservations)
    
    @staticmethod
    def get_book_availability(db: Session, book_id: int) -> BookAvailabilityInfo:
        """Get availability information for a book."""
        book = db.query(Book).filter(Book.id == book_id).first()
        if not book:
            raise ValueError("Book not found")
        
        # Count active loans
        active_loans = db.query(BookLoan).filter(
            and_(
                BookLoan.book_id == book_id,
                BookLoan.status.in_([LoanStatus.ACTIVE, LoanStatus.RENEWED, LoanStatus.OVERDUE])
            )
        ).count()
        
        # Count pending reservations
        pending_reservations = db.query(BookReservation).filter(
            and_(
                BookReservation.book_id == book_id,
                BookReservation.status == ReservationStatus.PENDING
            )
        ).count()
        
        # Calculate estimated availability
        estimated_availability = None
        if book.available_copies == 0 and pending_reservations > 0:
            # Find earliest due date
            earliest_due = db.query(BookLoan).filter(
                and_(
                    BookLoan.book_id == book_id,
                    BookLoan.status.in_([LoanStatus.ACTIVE, LoanStatus.RENEWED])
                )
            ).order_by(asc(BookLoan.due_date)).first()
            
            if earliest_due:
                estimated_availability = earliest_due.due_date
        
        return BookAvailabilityInfo(
            book_id=book_id,
            total_copies=book.total_copies,
            available_copies=book.available_copies,
            reserved_copies=book.reserved_copies,
            loaned_copies=active_loans,
            reservation_queue_length=pending_reservations,
            estimated_availability_date=estimated_availability,
            can_reserve=book.available_copies == 0 and pending_reservations < book.total_copies
        )
