from fastapi import Request
from fastapi.responses import JSONResponse


class ResourceNotFoundError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message


async def resource_not_found_handler(
    request: Request,
    exc: ResourceNotFoundError,
) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={
            "error": {
                "code": "RESOURCE_NOT_FOUND",
                "message": exc.message,
            }
        },
    )
