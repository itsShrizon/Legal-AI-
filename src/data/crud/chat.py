from sqlalchemy.orm import Session
from src.data.models import ChatSession, ChatMessage
from src.data.schemas import ChatSessionCreate
from typing import List

def create_chat_session(db: Session, user_id: int, session_in: ChatSessionCreate):
    db_session = ChatSession(**session_in.model_dump(), user_id=user_id)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def get_user_sessions(db: Session, user_id: int):
    return db.query(ChatSession).filter(ChatSession.user_id == user_id).all()

def add_message(db: Session, session_id: int, role: str, content: str, citations: str = None):
    db_message = ChatMessage(session_id=session_id, role=role, content=content, citations=citations)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message
