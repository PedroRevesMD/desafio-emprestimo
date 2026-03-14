from pydantic import BaseModel, Field, field_validator
from typing import Annotated, List, Optional
from app.core.enums import LoanTypeEnum, VALID_UFS 

class CustomerInput(BaseModel):
    age: Annotated[int, Field(ge=18, le=120, strict=True)]
    cpf: Annotated[str, Field(pattern=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$')]
    name: Annotated[str, Field(min_length=2, max_length=200)]
    income: Annotated[float, Field(gt=0)]
    location: Annotated[str, Field(min_length=2, max_length=2)]

    @field_validator('name', mode='before')
    @classmethod
    def strip_name(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator('location')
    @classmethod
    def validate_location(cls, uf: str) -> str:
        upper = uf.upper()
        if upper not in VALID_UFS:
            raise ValueError(f"'{uf}' não é uma UF brasileira válida.")
        return upper

class LoanTypeResponse(BaseModel):
    type: LoanTypeEnum
    interest_rate: int

class LoanResponse(BaseModel):
    customer: str
    loans: List[LoanTypeResponse]

class ErrorDetail(BaseModel):
    field: str
    message: str

class ErrorResponseContent(BaseModel):
    code: str
    message: str
    details: Optional[List[ErrorDetail]] = None

class ErrorResponse(BaseModel):
    error: ErrorResponseContent
