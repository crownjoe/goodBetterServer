from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, HttpUrl
from database import SessionLocal, User, engine, Base
from typing import List

app = FastAPI()

data_store = []

class UserLogin(BaseModel):
    user_id: str

class RequestData(BaseModel):
    Color: int
    Date: str  
    Weather: int
    Image: str
    Content: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if not db.query(User).filter(User.user_id == "yellow").first():
        db.add(User(user_id="yellow", color="yellow"))

    if not db.query(User).filter(User.user_id == "green").first():
        db.add(User(user_id="green", color="green"))
    db.commit()
    db.close()

@app.on_event("startup")
def on_startup():
    init_db()

@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.user_id == user.user_id).first()
    if db_user:
        if db_user.user_id == 'yellow':
            return 0
        else : #green
            return 1
    else:
        raise HTTPException(status_code = 400, detail = "유효하지 않는 사용자입니다.")
    
@app.post("/finish", response_model=List[RequestData])
def receive_and_return_all_data(request_data: RequestData):
    data_store.append(request_data)
    return data_store

@app.post("/search", response_model=List[RequestData])
def receive_and_return_all_data():
    return data_store


# @app.post("/comment", respom)


# FastAPI 서버 실행 시 초기화
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
