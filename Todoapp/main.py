from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException, Path, status

from .database import SessionLocal, engine
from .models import Base

from .routers import auth,todos,admin, users

app = FastAPI()

## create the database
Base.metadata.create_all(bind=engine)

@app.get("/healthy")
def healthy():
    return {"status": "healthy"}

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)
