from fastapi import APIRouter, Depends
from app.models.schemas import CustomerInput, LoanResponse, LoanTypeResponse
from app.services.loan_service import get_eligible_loans
from app.core.enums import LOAN_RATES
from app.models.database import log_request_response

router = APIRouter()

@router.post("/customer-loans", response_model=LoanResponse)
async def create_customer_loans(customer: CustomerInput):
    eligible_loan_enums = get_eligible_loans(customer)
    
    loans = [
        LoanTypeResponse(type=lt, interest_rate=LOAN_RATES[lt])
        for lt in eligible_loan_enums
    ]
    
    response = LoanResponse(
        customer=customer.name,
        loans=loans
    )
    
    log_request_response(customer, response)
    
    return response
