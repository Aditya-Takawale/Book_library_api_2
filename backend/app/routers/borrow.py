from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.borrow import BookBorrowRequest
from app.schemas.loan import BookLoanResponse
from app.services.loan_service import LoanService
from app.utils.dependencies import get_current_user
from app.schemas.user import UserResponse
from datetime import datetime, timedelta
import logging

logger = logging.getLogger("BorrowAPI")

router = APIRouter()

@router.post("/borrow", response_model=BookLoanResponse)
def borrow_book(
    borrow_request: BookBorrowRequest,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Allows the current logged-in user to borrow a book.
    """
    logger.info(f"User {current_user.id} requesting to borrow book {borrow_request.book_id}")
    
    # Create a loan for the current user
    loan_data = {
        "book_id": borrow_request.book_id,
        "due_date": datetime.now() + timedelta(days=14),  # Standard 14-day loan
        "notes": None
    }
    
    logger.info(f"Creating loan with data: {loan_data} for user_id: {current_user.id}")
    
    try:
        new_loan = LoanService.create_loan(db, loan_data, current_user.id)
        
        logger.info(f"Loan created successfully: {new_loan.id}")
        
        # Convert to response model
        response = BookLoanResponse.from_orm(new_loan)
        response.is_overdue = new_loan.is_overdue
        response.days_until_due = new_loan.days_until_due
        
        return response
    except ValueError as e:
        logger.error(f"ValueError creating loan for user {current_user.id}, book {borrow_request.book_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating loan for user {current_user.id}, book {borrow_request.book_id}: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        raise HTTPException(status_code=500, detail=f"Failed to create loan: {str(e)}")
