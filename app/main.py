from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from app.controllers.loan_controller import router as loan_router
from app.core.exceptions import (
    handle_validation_error,
    handle_http_exception,
    handle_internal_error
)
from app.models.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="Customer Loans API", lifespan=lifespan)

# Register exception handlers
app.add_exception_handler(RequestValidationError, handle_validation_error)
app.add_exception_handler(HTTPException,          handle_http_exception)
app.add_exception_handler(Exception,              handle_internal_error)

# Include routes
app.include_router(loan_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
