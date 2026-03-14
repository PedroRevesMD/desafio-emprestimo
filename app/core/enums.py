from enum import Enum


class LoanTypeEnum(str, Enum):
    PERSONAL = "PERSONAL"
    GUARANTEED = "GUARANTEED"
    CONSIGNMENT = "CONSIGNMENT"


LOAN_RATES = {
    LoanTypeEnum.PERSONAL: 4,
    LoanTypeEnum.GUARANTEED: 3,
    LoanTypeEnum.CONSIGNMENT: 2,
}

VALID_UFS = {
    "AC",
    "AL",
    "AP",
    "AM",
    "BA",
    "CE",
    "DF",
    "ES",
    "GO",
    "MA",
    "MT",
    "MS",
    "MG",
    "PA",
    "PB",
    "PR",
    "PE",
    "PI",
    "RJ",
    "RN",
    "RS",
    "RO",
    "RR",
    "SC",
    "SP",
    "SE",
    "TO",
}
