from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.api.dependencies import get_db, get_current_user
from src.data.schemas import QueryRequest, User, ChatSessionCreate
from src.services.rag_service import ask_question
from src.data.crud.chat import add_message, create_chat_session

router = APIRouter()

@router.post("/query")
def chat_endpoint(request: QueryRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # 1. Create Session if not exists (simplified logic)
    session_id = request.session_id
    if not session_id:
        chat_session = create_chat_session(db, user_id=current_user.id, session_in=ChatSessionCreate(title="New Query"))
        session_id = chat_session.id
    
    # 2. Save User Message
    add_message(db, session_id=session_id, role="user", content=request.query)
    
    # 3. Get Answer
    answer = ask_question(db, request.query)
    
    # 4. Save AI Response
    add_message(db, session_id=session_id, role="assistant", content=answer)
    
    return {"response": answer, "session_id": session_id}
