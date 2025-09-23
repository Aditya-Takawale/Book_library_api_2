"""
API routes for book loan and reservation management.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.schemas.loan import (
    BookLoanCreate, BookLoanUpdate, BookLoanResponse, BookLoanRenewal,
    BookReservationCreate, BookReservationUpdate, BookReservationResponse,
    LoanStatistics, ReservationStatistics, BookAvailabilityInfo,
    LoanStatus, ReservationStatus, LoanListResponse
)
from app.schemas.user import UserResponse
from app.services.loan_service import LoanService, ReservationService
from app.models.loan import BookLoan
from app.utils.rbac import (
    require_admin_user,
    require_librarian_user,
    require_member_user,
    log_access_attempt
)
from app.utils.dependencies import get_current_user
import logging

logger = logging.getLogger("LoanAPI")

router = APIRouter(prefix="/loans", tags=["Loans & Reservations"])

# Loan Management Endpoints
@router.post("/", response_model=BookLoanResponse)
async def create_loan(
    loan_data: BookLoanCreate,
    current_user: UserResponse = Depends(require_librarian_user),
    db: Session = Depends(get_db)
):
    """Create a new book loan (librarian/admin only)."""
    try:
        log_access_attempt(current_user, "loans", "create", True)
        loan = LoanService.create_loan(db, loan_data, current_user.id)
        
        # Convert to response model
        response = BookLoanResponse.from_orm(loan)
        response.is_overdue = loan.is_overdue
        response.days_until_due = loan.days_until_due
        
        # Add complete book information if available
        if loan.book:
            from app.schemas.loan import BookSummary
            from app.schemas.author import AuthorSummary
            
            # Create book object with authors
            book_authors = [
                AuthorSummary.from_orm(author) for author in loan.book.authors
            ] if loan.book.authors else []
            
            response.book = BookSummary(
                id=loan.book.id,
                title=loan.book.title,
                authors=book_authors
            )
        
        logger.info(f"Loan created by {current_user.email}: Book {loan_data.book_id} to User {loan_data.user_id}")
        return response
        
    except ValueError as e:
        log_access_attempt(current_user, "loans", "create", False, str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        log_access_attempt(current_user, "loans", "create", False, str(e))
        logger.error(f"Error creating loan: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create loan")

@router.put("/{loan_id}/return", response_model=BookLoanResponse)
async def return_book(
    loan_id: int,
    current_user: UserResponse = Depends(require_librarian_user),
    db: Session = Depends(get_db)
):
    """Process book return (librarian/admin only)."""
    try:
        loan = LoanService.return_book(db, loan_id, current_user.id)
        
        response = BookLoanResponse.from_orm(loan)
        response.is_overdue = loan.is_overdue
        response.days_until_due = loan.days_until_due
        
        # Add complete book information if available
        if loan.book:
            from app.schemas.loan import BookSummary
            from app.schemas.author import AuthorSummary
            
            # Create book object with authors
            book_authors = [
                AuthorSummary.from_orm(author) for author in loan.book.authors
            ] if loan.book.authors else []
            
            response.book = BookSummary(
                id=loan.book.id,
                title=loan.book.title,
                authors=book_authors
            )
        
        log_access_attempt(current_user, "loans", "return", True, f"Loan {loan_id}")
        logger.info(f"Book returned by {current_user.email}: Loan {loan_id}")
        return response
        
    except ValueError as e:
        log_access_attempt(current_user, "loans", "return", False, str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        log_access_attempt(current_user, "loans", "return", False, str(e))
        logger.error(f"Error returning book: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to return book")

@router.post("/{loan_id}/return", response_model=BookLoanResponse)
async def return_book_member(
    loan_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Process book return (members can return their own books)."""
    try:
        # Check if the loan belongs to the current user (unless they're admin/librarian)
        loan = db.query(BookLoan).filter(BookLoan.id == loan_id).first()
        if not loan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan not found")
        
        if loan.user_id != current_user.id and current_user.role not in ['Admin', 'Librarian']:
            log_access_attempt(current_user, "loans", "return", False, f"Not owner of loan {loan_id}")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can only return your own books")
        
        returned_loan = LoanService.return_book(db, loan_id, current_user.id)
        
        response = BookLoanResponse.from_orm(returned_loan)
        response.is_overdue = returned_loan.is_overdue
        response.days_until_due = returned_loan.days_until_due
        
        # Add complete book information if available
        if returned_loan.book:
            from app.schemas.loan import BookSummary
            from app.schemas.author import AuthorSummary
            
            # Create book object with authors
            book_authors = [
                AuthorSummary.from_orm(author) for author in returned_loan.book.authors
            ] if returned_loan.book.authors else []
            
            response.book = BookSummary(
                id=returned_loan.book.id,
                title=returned_loan.book.title,
                authors=book_authors
            )
        
        log_access_attempt(current_user, "loans", "return", True, f"Loan {loan_id}")
        logger.info(f"Book returned by {current_user.email}: Loan {loan_id}")
        return response
        
    except ValueError as e:
        log_access_attempt(current_user, "loans", "return", False, str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        log_access_attempt(current_user, "loans", "return", False, str(e))
        logger.error(f"Error returning book: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to return book")

@router.put("/{loan_id}/renew", response_model=BookLoanResponse)
async def renew_loan(
    loan_id: int,
    renewal_data: BookLoanRenewal,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Renew a book loan (member+ can renew their own loans)."""
    try:
        # Check if user owns the loan or is librarian/admin
        loan = db.query(BookLoan).filter(BookLoan.id == loan_id).first()
        if not loan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan not found")
        
        if loan.user_id != current_user.id and current_user.role.value not in ['admin', 'librarian']:
            log_access_attempt(current_user, "loans", "renew", False, f"Not owner of loan {loan_id}")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can only renew your own loans")
        
        renewed_loan = LoanService.renew_loan(db, loan_id, renewal_data.extension_days)
        
        response = BookLoanResponse.from_orm(renewed_loan)
        response.is_overdue = renewed_loan.is_overdue
        response.days_until_due = renewed_loan.days_until_due
        
        # Add complete book information if available
        if renewed_loan.book:
            from app.schemas.loan import BookSummary
            from app.schemas.author import AuthorSummary
            
            # Create book object with authors
            book_authors = [
                AuthorSummary.from_orm(author) for author in renewed_loan.book.authors
            ] if renewed_loan.book.authors else []
            
            response.book = BookSummary(
                id=renewed_loan.book.id,
                title=renewed_loan.book.title,
                authors=book_authors
            )
        
        log_access_attempt(current_user, "loans", "renew", True, f"Loan {loan_id}")
        logger.info(f"Loan renewed by {current_user.email}: Loan {loan_id}")
        return response
        
    except ValueError as e:
        log_access_attempt(current_user, "loans", "renew", False, str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        log_access_attempt(current_user, "loans", "renew", False, str(e))
        logger.error(f"Error renewing loan: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to renew loan")

@router.post("/{loan_id}/renew", response_model=BookLoanResponse)
async def renew_loan_member(
    loan_id: int,
    current_user: UserResponse = Depends(require_member_user),
    db: Session = Depends(get_db)
):
    """Renew a book loan with default extension (members can renew their own loans)."""
    try:
        # Check if user owns the loan or is librarian/admin
        loan = db.query(BookLoan).filter(BookLoan.id == loan_id).first()
        if not loan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan not found")
        
        if loan.user_id != current_user.id and current_user.role not in ['Admin', 'Librarian']:
            log_access_attempt(current_user, "loans", "renew", False, f"Not owner of loan {loan_id}")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can only renew your own loans")
        
        # Use default extension of 14 days
        renewed_loan = LoanService.renew_loan(db, loan_id, 14)
        
        response = BookLoanResponse.from_orm(renewed_loan)
        response.is_overdue = renewed_loan.is_overdue
        response.days_until_due = renewed_loan.days_until_due
        
        # Add complete book information if available
        if renewed_loan.book:
            from app.schemas.loan import BookSummary
            from app.schemas.author import AuthorSummary
            
            # Create book object with authors
            book_authors = [
                AuthorSummary.from_orm(author) for author in renewed_loan.book.authors
            ] if renewed_loan.book.authors else []
            
            response.book = BookSummary(
                id=renewed_loan.book.id,
                title=renewed_loan.book.title,
                authors=book_authors
            )
        
        log_access_attempt(current_user, "loans", "renew", True, f"Loan {loan_id}")
        logger.info(f"Loan renewed by {current_user.email}: Loan {loan_id}")
        return response
        
    except ValueError as e:
        log_access_attempt(current_user, "loans", "renew", False, str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        log_access_attempt(current_user, "loans", "renew", False, str(e))
        logger.error(f"Error renewing loan: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to renew loan")

@router.get("/", response_model=LoanListResponse)
async def get_all_loans(
    skip: int = Query(0, ge=0, description="Number of loans to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of loans to return"),
    status: Optional[LoanStatus] = Query(None, description="Filter by loan status"),
    search: Optional[str] = Query(None, description="Search term for user or book"),
    current_user: UserResponse = Depends(require_librarian_user),
    db: Session = Depends(get_db)
):
    """Get all loans with pagination (librarian/admin only)."""
    try:
        total, loans = LoanService.get_all_loans(db, skip=skip, limit=limit, status=status, search=search)
        
        response_loans = []
        for loan in loans:
            response = BookLoanResponse.from_orm(loan)
            response.is_overdue = loan.is_overdue
            response.days_until_due = loan.days_until_due
            
            # Add complete book information if available
            if loan.book:
                from app.schemas.loan import BookSummary
                from app.schemas.author import AuthorSummary
                
                # Create book object with authors
                book_authors = [
                    AuthorSummary.from_orm(author) for author in loan.book.authors
                ] if loan.book.authors else []
                
                response.book = BookSummary(
                    id=loan.book.id,
                    title=loan.book.title,
                    authors=book_authors
                )
            
            if loan.user:
                response.user_email = loan.user.email
            response_loans.append(response)
        
        log_access_attempt(current_user, "loans", "view_all", True)
        return LoanListResponse(total=total, loans=response_loans)
        
    except Exception as e:
        logger.error(f"Error fetching all loans: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch loans")

@router.get("/user/{user_id}", response_model=List[BookLoanResponse])
async def get_user_loans(
    user_id: int,
    status: Optional[LoanStatus] = Query(None, description="Filter by loan status"),
    current_user: UserResponse = Depends(require_member_user),
    db: Session = Depends(get_db)
):
    """Get loans for a specific user."""
    # Users can only see their own loans unless they're librarian/admin
    if user_id != current_user.id and current_user.role not in ['Admin', 'Librarian']:
        log_access_attempt(current_user, "loans", "view", False, f"Unauthorized access to user {user_id} loans")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can only view your own loans")
    
    try:
        loans = LoanService.get_user_loans(db, user_id, status)
        
        response_loans = []
        for loan in loans:
            response = BookLoanResponse.from_orm(loan)
            response.is_overdue = loan.is_overdue
            response.days_until_due = loan.days_until_due
            
            # Add complete book information if available
            if loan.book:
                from app.schemas.loan import BookSummary
                from app.schemas.author import AuthorSummary
                
                # Create book object with authors
                book_authors = [
                    AuthorSummary.from_orm(author) for author in loan.book.authors
                ] if loan.book.authors else []
                
                response.book = BookSummary(
                    id=loan.book.id,
                    title=loan.book.title,
                    authors=book_authors
                )
            
            response_loans.append(response)
        
        log_access_attempt(current_user, "loans", "view", True, f"User {user_id} loans")
        return response_loans
        
    except Exception as e:
        logger.error(f"Error fetching user loans: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch loans")

@router.get("/my", response_model=List[BookLoanResponse])
async def get_my_loans(
    status: Optional[LoanStatus] = Query(None, description="Filter by loan status"),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get loans for the current authenticated user."""
    try:
        logger.info(f"Fetching loans for user {current_user.email} (ID: {current_user.id})")
        loans = LoanService.get_user_loans(db, current_user.id, status)
        
        response_loans = []
        for loan in loans:
            response = BookLoanResponse.from_orm(loan)
            response.is_overdue = loan.is_overdue
            response.days_until_due = loan.days_until_due
            
            # Add complete book information if available
            if loan.book:
                from app.schemas.loan import BookSummary
                from app.schemas.author import AuthorSummary
                
                # Create book object with authors
                book_authors = [
                    AuthorSummary.from_orm(author) for author in loan.book.authors
                ] if loan.book.authors else []
                
                response.book = BookSummary(
                    id=loan.book.id,
                    title=loan.book.title,
                    authors=book_authors
                )
            
            response_loans.append(response)
        
        logger.info(f"Retrieved {len(response_loans)} loans for user {current_user.email}")
        return response_loans
        
    except Exception as e:
        logger.error(f"Error fetching my loans: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch my loans")

@router.get("/overdue", response_model=List[BookLoanResponse])
async def get_overdue_loans(
    current_user: UserResponse = Depends(require_librarian_user),
    db: Session = Depends(get_db)
):
    """Get all overdue loans (librarian/admin only)."""
    try:
        loans = LoanService.get_overdue_loans(db)
        
        response_loans = []
        for loan in loans:
            response = BookLoanResponse.from_orm(loan)
            response.is_overdue = loan.is_overdue
            response.days_until_due = loan.days_until_due
            
            # Add complete book information if available
            if loan.book:
                from app.schemas.loan import BookSummary
                from app.schemas.author import AuthorSummary
                
                # Create book object with authors
                book_authors = [
                    AuthorSummary.from_orm(author) for author in loan.book.authors
                ] if loan.book.authors else []
                
                response.book = BookSummary(
                    id=loan.book.id,
                    title=loan.book.title,
                    authors=book_authors
                )
            
            if loan.user:
                response.user_email = loan.user.email
            response_loans.append(response)
        
        log_access_attempt(current_user, "loans", "view_overdue", True)
        return response_loans
        
    except Exception as e:
        logger.error(f"Error fetching overdue loans: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch overdue loans")

@router.post("/update-overdue-status")
async def update_overdue_status(
    current_user: UserResponse = Depends(require_librarian_user),
    db: Session = Depends(get_db)
):
    """Update overdue loan statuses (librarian/admin only)."""
    try:
        updated_count = LoanService.update_overdue_status(db)
        
        log_access_attempt(current_user, "loans", "update_overdue", True, f"Updated {updated_count} loans")
        return {"message": f"Updated {updated_count} loans to overdue status"}
        
    except Exception as e:
        logger.error(f"Error updating overdue status: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update overdue status")

@router.get("/statistics", response_model=LoanStatistics)
async def get_loan_statistics(
    current_user: UserResponse = Depends(require_librarian_user),
    db: Session = Depends(get_db)
):
    """Get loan statistics (librarian/admin only)."""
    try:
        stats = LoanService.get_loan_statistics(db)
        log_access_attempt(current_user, "loans", "view_statistics", True)
        return stats
        
    except Exception as e:
        logger.error(f"Error fetching loan statistics: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch statistics")

# Reservation Management Endpoints
@router.post("/reservations", response_model=BookReservationResponse)
async def create_reservation(
    reservation_data: BookReservationCreate,
    current_user: UserResponse = Depends(require_member_user),
    db: Session = Depends(get_db)
):
    """Create a new book reservation (member+ only)."""
    try:
        # Users can only create reservations for themselves unless they're librarian/admin
        if reservation_data.user_id != current_user.id and current_user.role.value not in ['admin', 'librarian']:
            log_access_attempt(current_user, "reservations", "create", False, "Unauthorized user_id")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can only create reservations for yourself")
        
        reservation = ReservationService.create_reservation(db, reservation_data)
        
        response = BookReservationResponse.from_orm(reservation)
        response.is_expired = reservation.is_expired
        # Calculate queue position
        response.queue_position = reservation.calculate_queue_position(db)
        
        log_access_attempt(current_user, "reservations", "create", True)
        logger.info(f"Reservation created by {current_user.email}: Book {reservation_data.book_id}")
        return response
        
    except ValueError as e:
        log_access_attempt(current_user, "reservations", "create", False, str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        log_access_attempt(current_user, "reservations", "create", False, str(e))
        logger.error(f"Error creating reservation: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create reservation")

@router.delete("/reservations/{reservation_id}")
async def cancel_reservation(
    reservation_id: int,
    current_user: UserResponse = Depends(require_member_user),
    db: Session = Depends(get_db)
):
    """Cancel a reservation."""
    try:
        # Users can only cancel their own reservations unless they're librarian/admin
        user_id = current_user.id if current_user.role.value not in ['admin', 'librarian'] else None
        
        reservation = ReservationService.cancel_reservation(db, reservation_id, user_id)
        
        log_access_attempt(current_user, "reservations", "cancel", True, f"Reservation {reservation_id}")
        return {"message": "Reservation cancelled successfully"}
        
    except ValueError as e:
        log_access_attempt(current_user, "reservations", "cancel", False, str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        log_access_attempt(current_user, "reservations", "cancel", False, str(e))
        logger.error(f"Error cancelling reservation: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to cancel reservation")

@router.get("/reservations/user/{user_id}", response_model=List[BookReservationResponse])
async def get_user_reservations(
    user_id: int,
    status: Optional[ReservationStatus] = Query(None, description="Filter by reservation status"),
    current_user: UserResponse = Depends(require_member_user),
    db: Session = Depends(get_db)
):
    """Get reservations for a specific user."""
    # Users can only see their own reservations unless they're librarian/admin
    if user_id != current_user.id and current_user.role.value not in ['admin', 'librarian']:
        log_access_attempt(current_user, "reservations", "view", False, f"Unauthorized access to user {user_id} reservations")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can only view your own reservations")
    
    try:
        reservations = ReservationService.get_user_reservations(db, user_id, status)
        
        response_reservations = []
        for reservation in reservations:
            response = BookReservationResponse.from_orm(reservation)
            response.is_expired = reservation.is_expired
            response.queue_position = reservation.calculate_queue_position(db)
            # Add book title if available
            if reservation.book:
                response.book_title = reservation.book.title
            response_reservations.append(response)
        
        log_access_attempt(current_user, "reservations", "view", True, f"User {user_id} reservations")
        return response_reservations
        
    except Exception as e:
        logger.error(f"Error fetching user reservations: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch reservations")

@router.get("/books/{book_id}/availability", response_model=BookAvailabilityInfo)
async def get_book_availability(
    book_id: int,
    current_user: UserResponse = Depends(require_member_user),
    db: Session = Depends(get_db)
):
    """Get availability information for a book."""
    try:
        availability = ReservationService.get_book_availability(db, book_id)
        log_access_attempt(current_user, "books", "view_availability", True, f"Book {book_id}")
        return availability
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching book availability: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch availability")

@router.post("/reservations/expire-old")
async def expire_old_reservations(
    current_user: UserResponse = Depends(require_librarian_user),
    db: Session = Depends(get_db)
):
    """Expire old reservations (librarian/admin only)."""
    try:
        expired_count = ReservationService.expire_old_reservations(db)
        
        log_access_attempt(current_user, "reservations", "expire_old", True, f"Expired {expired_count} reservations")
        return {"message": f"Expired {expired_count} old reservations"}
        
    except Exception as e:
        logger.error(f"Error expiring reservations: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to expire reservations")
