from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
from starlette import status
import os

from .db import Base
from .db import engine
from .routers.auth.auth import router as auth_router
from .routers.todo.todo import router as todo_router

app = FastAPI()

# create db
Base.metadata.create_all(bind=engine)

script_dir = os.path.dirname(__file__)
st_ab_file_path = os.path.join(script_dir, "frontend/static")

#connect frontend with main.py
app.mount("/static", StaticFiles(directory=st_ab_file_path), name="static")

app.include_router(auth_router)
app.include_router(todo_router)

@app.get("/")
def root(request: Request):
    return RedirectResponse(url="/todo/todo-page", status_code=status.HTTP_302_FOUND)