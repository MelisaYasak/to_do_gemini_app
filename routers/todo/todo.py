from fastapi import Body, Depends, Path, HTTPException, APIRouter, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from db import Base, SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from models.m_todo.todo import Todo
from starlette import status
from starlette.responses import RedirectResponse
from routers.auth.auth import get_current_user
from dotenv import load_dotenv
import google.generativeai as genai
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
import markdown
from bs4 import BeautifulSoup

router = APIRouter( prefix="/todo", tags=["ToDo"])

templates= Jinja2Templates(directory="frontend/templates")
#for creating post methods, you should create Request model which inherted from BaseModel
class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=1000)
    priority: int = Field(gt=0, lt=6)
    completed: bool

#use SessionMaker in db.py with SessionLocal to connect database
def get_db():
    db = SessionLocal()
    try:
        # It is similar to return in that it returns something from the function.
        # But functions using ‘yeild’ are called ‘Generater Function’.
        # While ‘return’ returns a single value, ‘yeild’ can return successive values. You can iterrate into the method.
        yield db
    finally:
        # to close Session
        db.close()
# From now, all methods to be written will ‘depends’ on this method.
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

#redirect to login method
def redirect_to_login():
    redirect_response = RedirectResponse(url="/auth/login-page", status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie("access_token")
    return redirect_response

#Bind todo-page with backend
@router.get("/todo-page")
async def todo_page(request: Request, db: db_dependency):
    try:    
        user = await get_current_user(request.cookies.get("access_token"))
        if user is None:
            return redirect_to_login()
        todos = db.query(Todo).filter(Todo.owner_id == user.get(id)).all()
        return templates.TemplateResponse("todo.html", {"request": request, "todos": todos, "user": user})
    except:
        return redirect_to_login()
    

#Todo adding
@router.get("/add-todo-page")
async def add_todo_page(request: Request):
    try:    
        user = await get_current_user(request.cookies.get("access_token"))
        if user is None:
            return redirect_to_login()

        return templates.TemplateResponse("add-todo.html", {"request": request, "user": user})
    except:
        return redirect_to_login()


# Todo Editing
@router.get("/edit-todo-page/{todo-id}")
async def todo_page(request: Request, todo_id: int, db: db_dependency):
    try: 
        user = await get_current_user(request.cookies.get("access_token"))
        if user is None:
            return redirect_to_login()
        todo = db.query(Todo).filter(Todo.id == todo_id).first()

        return templates.TemplateResponse("edit-todo.html", {"request": request, "todo": todo, "user": user})
    except:
        return redirect_to_login()

def markdown_to_text(mardown_str):
    html = markdown.markdown(mardown_str)
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text()
    return text

# create todo description with gemini
def create_desc_with_gemini(todo_str: str):
    load_dotenv()
    genai.configure(api_key=os.environ.get('GOOGLE_API_KEY'))
    llm = ChatGoogleGenerativeAI(model='gemini-pro')
    response = llm.invoke(
        [
            HumanMessage(content="""
                         I will provide a short to-do item, and I want you to expand it into a detailed and comprehensive description. 
                         Your description should clarify the task, its purpose, and any necessary steps to complete it. 
                         If relevant, include deadlines, tools, or considerations. 
                         My next message will be the to-do item."""),
            HumanMessage(content=todo_str),   
        ]
    )
    return markdown_to_text(response.content)

@router.get("/")
async def get_by_user_id(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials") 
    return db.query(Todo).filter(Todo.owner_id == user.get(id)).all()

#filter by id
@router.get("/get/{id}", status_code=status.HTTP_200_OK)
async def get_by_id(user: user_dependency, db: db_dependency, id: int = Path(gt=0) ):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    
    todo = db.query(Todo).filter(Todo.id == id).filter(Todo.owner_id == user.get(id)).first()
    
    if todo:
        return todo
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ToDo not Found!")

@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db: db_dependency, request: TodoRequest):
    # create a new todo
    # Todo(title=request.title, description=request.description, priority=request.priority, complete=request.complete)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    
    new_todo = Todo(**request.model_dump(), owner_id=user.get(id))
    new_todo.description = create_desc_with_gemini(new_todo.description)
    db.add(new_todo)
    db.commit()


# update todo by id
@router.put("/update/{id}")
async def update_todo(user: user_dependency,
                      db: db_dependency, 
                      request: TodoRequest,
                      id: int = Path(gt=0) ):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    
    todo = db.query(Todo).filter(Todo.id == id).filter(Todo.owner_id == user.get(id)).first()
    if todo:
        todo.title = request.title
        todo.description = request.description
        todo.priority = request.priority
        todo.completed = request.completed
        db.add(todo)
        db.commit()
        return {"message": "Todo updated successfully"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ToDo not Found!")
    
# delete by id
@router.delete("/delete/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, id: int = Path(gt=0) ):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    todo = db.query(Todo).filter(Todo.id == id).filter(Todo.owner_id == user.get(id)).first()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ToDo not Found!")
    db.delete(todo)
    db.commit()
