"""
Book Loan and Reservation models for library management.
"""
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Text, Index, CheckConstraint, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.db import Base
from datetime import datetime, timedelta
import enum

class LoanStatus(enum.Enum):
    ACTIVE = "Active"
    RETURNED = "Returned"
    OVERDUE = "Overdue"
    RENEWED = "Renewed"
    LOST = "Lost"
    DAMAGED = "Damaged"

class ReservationStatus(enum.Enum):
    PENDING = "Pending"
    READY = "Ready"
    FULFILLED = "Fulfilled"
    CANCELLED = "Cancelled"
    EXPIRED = "Expired"

class BookLoan(Base):
    """Model for tracking book loans/checkouts."""
    __tablename__ = "book_loans"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum(LoanStatus), default=LoanStatus.ACTIVE, nullable=False)
    
    # Loan dates
    loan_date = Column(DateTime, nullable=False, default=func.now())
    due_date = Column(DateTime, nullable=False)
    return_date = Column(DateTime, nullable=True)
    
    # Administrative fields
    notes = Column(Text, nullable=True)
    renewal_count = Column(Integer, default=0, nullable=False)
    fine_amount = Column(Integer, default=0, nullable=False)  # In cents (for compatibility)
    condition_at_loan = Column(Text, nullable=True)
    condition_at_return = Column(Text, nullable=True)
    late_fee = Column(Integer, default=0, nullable=False)  # In cents
    
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    book = relationship("Book", back_populates="loans")
    user = relationship("User", foreign_keys=[user_id], back_populates="borrowed_books")
    librarian = relationship("User", foreign_keys=[created_by], overlaps="created_loans")

    # Constraints and indexes
    __table_args__ = (
        CheckConstraint('due_date > loan_date', name='due_date_after_loan_date'),
        CheckConstraint('return_date IS NULL OR return_date >= loan_date', name='return_date_after_loan_date'),
        CheckConstraint('late_fee >= 0', name='non_negative_late_fee'),
        Index('idx_loan_user_status', 'user_id', 'status'),
        Index('idx_loan_book_status', 'book_id', 'status'),
        Index('idx_loan_due_date', 'due_date'),
        Index('idx_loan_status_due', 'status', 'due_date'),
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set default due date to 2 weeks from loan date
        if 'due_date' not in kwargs and 'loan_date' in kwargs:
            self.due_date = kwargs['loan_date'] + timedelta(days=14)
        elif 'due_date' not in kwargs:
            self.due_date = datetime.utcnow() + timedelta(days=14)

    @property
    def is_overdue(self) -> bool:
        """Check if loan is overdue."""
        return (self.status == LoanStatus.ACTIVE and 
                self.due_date < datetime.utcnow())

    @property
    def days_overdue(self) -> int:
        """Calculate number of days overdue."""
        if not self.is_overdue:
            return 0
        return (datetime.utcnow() - self.due_date).days

    @property
    def days_until_due(self) -> int:
        """Calculate number of days until due."""
        if self.return_date:  # Already returned
            return 0
        days_remaining = (self.due_date - datetime.utcnow()).days
        return max(0, days_remaining)

    @property
    def loan_duration_days(self) -> int:
        """Calculate loan duration in days."""
        end_date = self.return_date or datetime.utcnow()
        return (end_date - self.loan_date).days

    def calculate_late_fee(self, fee_per_day: int = 50) -> int:
        """Calculate late fee in cents."""
        if not self.is_overdue:
            return 0
        return self.days_overdue * fee_per_day

    def mark_returned(self, condition: str = None, librarian_id: int = None):
        """Mark loan as returned."""
        self.status = LoanStatus.RETURNED
        self.return_date = datetime.utcnow()
        if condition:
            self.condition_at_return = condition
        if self.is_overdue:
            self.late_fee = self.calculate_late_fee()

    def __repr__(self):
        return f"<BookLoan(id={self.id}, book_id={self.book_id}, user_id={self.user_id}, status='{self.status.value}')>"


class BookReservation(Base):
    """Model for tracking book reservations."""
    __tablename__ = "book_reservations"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum(ReservationStatus), default=ReservationStatus.PENDING, nullable=False)
    
    # Reservation dates
    reservation_date = Column(DateTime, nullable=False, default=func.now())
    expiry_date = Column(DateTime, nullable=False)
    pickup_date = Column(DateTime, nullable=True)
    
    # Administrative fields
    notes = Column(Text, nullable=True)
    priority = Column(Integer, default=1, nullable=False)  # 1 = normal, 2 = high, 3 = urgent
    
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    book = relationship("Book", back_populates="reservations")
    user = relationship("User", foreign_keys=[user_id])
    librarian = relationship("User", foreign_keys=[created_by])

    # Constraints and indexes
    __table_args__ = (
        CheckConstraint('expiry_date > reservation_date', name='expiry_after_reservation'),
        CheckConstraint('pickup_date IS NULL OR pickup_date >= reservation_date', name='pickup_after_reservation'),
        CheckConstraint('priority >= 1 AND priority <= 3', name='valid_priority'),
        Index('idx_reservation_user_status', 'user_id', 'status'),
        Index('idx_reservation_book_status', 'book_id', 'status'),
        Index('idx_reservation_expiry', 'expiry_date'),
        Index('idx_reservation_priority', 'priority', 'reservation_date'),
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set default expiry date to 7 days from reservation date
        if 'expiry_date' not in kwargs and 'reservation_date' in kwargs:
            self.expiry_date = kwargs['reservation_date'] + timedelta(days=7)
        elif 'expiry_date' not in kwargs:
            self.expiry_date = datetime.utcnow() + timedelta(days=7)

    @property
    def is_expired(self) -> bool:
        """Check if reservation is expired."""
        return (self.status in [ReservationStatus.PENDING, ReservationStatus.READY] and 
                self.expiry_date < datetime.utcnow())

    @property
    def queue_position(self) -> int:
        """Get position in reservation queue (would need database query)."""
        # This would typically be calculated by the service layer
        return 1

    def mark_ready(self):
        """Mark reservation as ready for pickup."""
        self.status = ReservationStatus.READY
        # Extend expiry by 3 days when ready
        self.expiry_date = datetime.utcnow() + timedelta(days=3)

    def mark_fulfilled(self):
        """Mark reservation as fulfilled."""
        self.status = ReservationStatus.FULFILLED
        self.pickup_date = datetime.utcnow()

    def cancel(self):
        """Cancel the reservation."""
        self.status = ReservationStatus.CANCELLED

    def __repr__(self):
        return f"<BookReservation(id={self.id}, book_id={self.book_id}, user_id={self.user_id}, status='{self.status.value}')>"
