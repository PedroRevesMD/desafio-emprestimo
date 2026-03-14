from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from app.models.schemas import ErrorResponse, ErrorResponseContent, ErrorDetail


async def handle_validation_error(request: Request, exc: RequestValidationError):
    is_json_error = any(
        error.get("type") in ["json_invalid", "value_error.jsondecode"]
        for error in exc.errors()
    )

    if is_json_error:
        content = ErrorResponse(
            error=ErrorResponseContent(
                code="BAD_REQUEST",
                message="O corpo da requisição é inválido ou não é um JSON bem-formado.",
            )
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content=content.model_dump()
        )

    details = []
    for error in exc.errors():
        field = ".".join([str(loc) for loc in error["loc"] if loc != "body"])
        details.append(ErrorDetail(field=field or "request", message=error["msg"]))

    content = ErrorResponse(
        error=ErrorResponseContent(
            code="VALIDATION_ERROR",
            message="Um ou mais campos enviados são inválidos.",
            details=details,
        )
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, content=content.model_dump()
    )


async def handle_http_exception(request: Request, exc: HTTPException):
    code_map = {
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        400: "BAD_REQUEST",
    }

    code = code_map.get(exc.status_code, "HTTP_ERROR")
    message = exc.detail

    if exc.status_code == 404 and (message == "Not Found" or not message):
        message = "A rota solicitada não existe."
    elif exc.status_code == 405:
        message = "O método HTTP utilizado não é permitido para esta rota."
    elif exc.status_code == 400 and (message == "Bad Request" or not message):
        message = "O corpo da requisição é inválido ou não é um JSON bem-formado."

    content = ErrorResponse(error=ErrorResponseContent(code=code, message=message))
    return JSONResponse(status_code=exc.status_code, content=content.model_dump())


async def handle_internal_error(request: Request, exc: Exception):
    content = ErrorResponse(
        error=ErrorResponseContent(
            code="INTERNAL_SERVER_ERROR",
            message="Ocorreu um erro inesperado. Por favor, tente novamente mais tarde.",
        )
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=content.model_dump()
    )
