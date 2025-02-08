from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
from starlette import status

from db import Base
from db import engine
from routers.auth.auth import router as auth_router
from routers.todo.todo import router as todo_router
import bcrypt
print(dir(bcrypt))


app = FastAPI()

# create db
Base.metadata.create_all(bind=engine)

#connect frontend with main.py
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

app.include_router(auth_router)
app.include_router(todo_router)

@app.get("/")
def root(request: Request):
    return RedirectResponse(url="/todo/todo-page", status_code=status.HTTP_302_FOUND)