from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import StaticPool
from fastapi import status
from ..main import app
from ..routers.todos import get_db,get_current_user
from fastapi.testclient import TestClient
from types import SimpleNamespace
import pytest
from ..models import Todos


from ..database import Base
SQLALCHEMY_DATABASE_URL='sqlite:///./testdb.db'
engine= create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False},
    poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#Create tables in the test database
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

def override_get_current_user():
    return SimpleNamespace(
        id=1,
        username="namit",
        user_role="admin"
    )
#Whenever an endpoint asks for get_db, use override_get_db instead.”
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client= TestClient(app)

@pytest.fixture(autouse=True)
def test_todos():
    todo=Todos(id=1, title="Test Todo", 
               description="This is a test todo", 
               priority=3, complete=False, owner_id=1)
    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield todo
    
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos"))
        connection.commit()
def test_read_all_authenticated():
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'complete': False, 
                                'description': 'This is a test todo', 'id': 1,
                                  'owner_id': 1, 'priority': 3, 'title': 'Test Todo'}]
    
def test_read_one_authenticated():
    response = client.get("/todo/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'complete': False, 
                                'description': 'This is a test todo', 'id': 1,
                                  'owner_id': 1, 'priority': 3, 'title': 'Test Todo'}
    
def test_read_one_not_found():
    response = client.get("/todo/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo with the id 999 is not available"}

def test_create_todo_authenticated(test_todos):
    response = client.post("/todo/", json={
        "title": "New Todo",
        "description": "This is a new todo",
        "priority": 2,
        "complete": False
    })
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {'complete': False, 
                                'description': 'This is a new todo', 'id': 2,
                                  'owner_id': 1, 'priority': 2, 'title': 'New Todo'}
    db= TestingSessionLocal()
    # Query the database to check if the todo was created
    todo = db.query(Todos).filter(Todos.id == 2).first()
    # Assert that the todo was created in the database
    assert todo is not None
    assert todo.title == "New Todo" 
    assert todo.description == "This is a new todo"
    assert todo.priority == 2
    assert todo.complete == False
    assert todo.owner_id == 1


def test_update_todo_authenticated(test_todos):
    response = client.put("/todo/1", json={
        "title": "Updated Todo",
        "description": "This is an updated todo",
        "priority": 1,
        "complete": True
    })
    assert response.status_code == status.HTTP_204_NO_CONTENT
    # Assert that the response body is empty    assert response.content == b''
    db= TestingSessionLocal()
    # Query the database to check if the todo was updated
    todo = db.query(Todos).filter(Todos.id == 1).first()
    # Assert that the todo was updated in the database
    assert todo is not None
    assert todo.title == "Updated Todo" 
    assert todo.description == "This is an updated todo"
    assert todo.priority == 1
    assert todo.complete == True

def test_update_todo_not_found():
    response = client.put("/todo/999", json={
        "title": "Updated Todo",
        "description": "This is an updated todo",
        "priority": 1,
        "complete": True
    })
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo with the id 999 is not available"}

def test_delete_todo_authenticated(test_todos):
    response = client.delete("/todo/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db= TestingSessionLocal()
    # Query the database to check if the todo was deleted
    todo = db.query(Todos).filter(Todos.id == 1).first()
    # Assert that the todo was deleted from the database
    assert todo is None

def test_delete_todo_not_found():
    response = client.delete("/todo/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo with the id 999 is not available"}