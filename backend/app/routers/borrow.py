from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.borrow import BookBorrowRequest
from app.schemas.loan import BookLoanResponse
from app.services.loan_service import LoanService
from app.utils.dependencies import get_current_user
from app.schemas.user import UserResponse
from datetime import datetime, timedelta

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
    # Create a loan for the current user
    loan_data = {
        "book_id": borrow_request.book_id,
        "user_id": current_user.id,
        "due_date": datetime.now() + timedelta(days=14)  # Standard 14-day loan
    }
    
    try:
        # Note: The create_loan service method might need adjustment
        # if it strictly requires a librarian_id for logging/validation.
        # For now, we'll pass the user's own ID.
        new_loan = LoanService.create_loan(db, loan_data, current_user.id)
        return new_loan
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred while borrowing the book.")
