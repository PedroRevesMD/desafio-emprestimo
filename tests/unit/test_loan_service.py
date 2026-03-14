import pytest
from app.services.loan_service import get_eligible_loans
from app.models.schemas import CustomerInput
from app.core.enums import LoanTypeEnum

@pytest.mark.parametrize("income, age, location, expected", [
    (5001, 40, "RJ", [LoanTypeEnum.CONSIGNMENT]),
    (10000, 18, "AM", [LoanTypeEnum.CONSIGNMENT]),
    (5000, 40, "MG", [LoanTypeEnum.CONSIGNMENT, LoanTypeEnum.GUARANTEED]),
    (3000, 40, "MG", [LoanTypeEnum.CONSIGNMENT, LoanTypeEnum.GUARANTEED]),
    (4000, 29, "SP", [LoanTypeEnum.CONSIGNMENT, LoanTypeEnum.GUARANTEED]),
    (4000, 35, "RJ", [LoanTypeEnum.CONSIGNMENT, LoanTypeEnum.GUARANTEED]),
    (2999, 29, "SP", []),
    (2999, 40, "RJ", []),
    (4000, 30, "SP", [LoanTypeEnum.CONSIGNMENT, LoanTypeEnum.GUARANTEED]),
    (2000, 25, "SP", []),
])
def test_get_eligible_loans_logic(income, age, location, expected):
    customer = CustomerInput(
        age=age,
        cpf="123.456.789-09",
        name="Test Customer",
        income=income,
        location=location
    )
    result = get_eligible_loans(customer)
    assert sorted(result) == sorted(expected)
