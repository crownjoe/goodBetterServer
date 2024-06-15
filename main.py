from uuid import UUID, uuid4
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, HttpUrl
from database import SessionLocal, User, engine, Base
from typing import Dict, List

app = FastAPI()

data_store = []

class UserLogin(BaseModel):
    user_id: str

class CommunityRequestData(BaseModel):
    id: str
    Color: int
    Date: str  
    Weather: int
    Image: str
    Content: str

class CommentRequestData(BaseModel):
    item_id: str
    comment: str

class searchCommentRequestData(BaseModel):
    item_id: str

comment_store: Dict[str, List[CommentRequestData]] = {}

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

# 유저 코드 입력해서 로그인
@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.user_id == user.user_id).first()
    if db_user:
        if db_user.user_id == 'yellow':
            return {"value": 0}
        else : #green
            return {"value": 1}
    else:
        raise HTTPException(status_code = 400, detail = "유효하지 않는 사용자입니다.")

# 사진 일기 작성 완료 & 커뮤니티 연결
@app.post("/finish", response_model=List[CommunityRequestData])
def receive_and_return_all_data(request_data: CommunityRequestData):
    data_store.append(request_data)
    return data_store

# 커뮤니티 조회
@app.post("/search", response_model=List[CommunityRequestData])
def receive_and_return_all_data():
    return data_store

# 댓글 작성 & 해당 게시글 댓글들 모두 반환
@app.post("/writeComment", response_model=List[CommentRequestData]) 
def add_comment(comment_data: CommentRequestData):

    item_id = comment_data.item_id

    if item_id not in comment_store:
        comment_store[item_id] = []
    
    comment_store[item_id].append(comment_data)

    return comment_store[item_id]

# 댓글 전체 조회
@app.post("/searchComment", response_model=List[str])  
def search_comments(comment_data: searchCommentRequestData):

    item_id = comment_data.item_id

    if item_id not in comment_store:
        raise HTTPException(status_code=404, detail="Item not found")
    
    comments = [comment.comment for comment in comment_store[item_id]]
    return comments


# 서버 초기화
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
