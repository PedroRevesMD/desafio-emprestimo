from typing import List
from app.core.enums import LoanTypeEnum
from app.models.schemas import CustomerInput

def get_eligible_loans(customer: CustomerInput) -> List[LoanTypeEnum]:
    loans = []
    if customer.income > 5000:
        return [LoanTypeEnum.CONSIGNMENT]
    
    if customer.income < 3000:
        return []

    condition_a = 3000 <= customer.income <= 5000
    
    condition_b = customer.age < 30 and customer.location == "SP"
    
    if condition_a or condition_b:
        loans.extend([LoanTypeEnum.CONSIGNMENT, LoanTypeEnum.GUARANTEED])
        
    return loans
