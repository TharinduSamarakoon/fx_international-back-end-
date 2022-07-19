import uvicorn

from fastapi import FastAPI,HTTPException
from fastapi.exceptions import RequestValidationError
from starlette.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles

from .utils import startup
from .db.mongodb_utils import close_mongo_connection
from .api.routes.api import router
from .config import API_PREFIX, VERSION, DEBUG, API_NAME
from .api.errors.http_errors import http_error_handler
from .api.errors.validation_errors import http422_error_handler

app = FastAPI(version=VERSION,
              debug=DEBUG,
              description=f'This is an auto generated document for the {API_NAME} service',
              openapi_url=f'{API_PREFIX}/openapi.json',
              docs_url=f'{API_PREFIX}/docs'
              )

origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.add_event_handler("startup", startup)
app.add_event_handler("shutdown", close_mongo_connection)

app.add_exception_handler(HTTPException, http_error_handler)
app.add_exception_handler(RequestValidationError, http422_error_handler)

app.include_router(router, prefix=API_PREFIX)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
