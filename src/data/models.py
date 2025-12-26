from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, ARRAY, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.data.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    sessions = relationship("ChatSession", back_populates="owner")

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, default="New Conversation") 
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"))
    role = Column(String)  # "user" or "assistant"
    content = Column(Text) 
    
    # Metadata for RAG transparency
    citations = Column(Text, nullable=True) # JSON string or specific format
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("ChatSession", back_populates="messages")

class LegalDocument(Base):
    """Represents a file like 'Anomaly_in_Constitution.txt'"""
    __tablename__ = "legal_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True)
    title = Column(String)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    
    chunks = relationship("LegalChunk", back_populates="document")

class LegalChunk(Base):
    """Represents the specific text chunks"""
    __tablename__ = "legal_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    chunk_id = Column(String, unique=True, index=True)
    document_id = Column(Integer, ForeignKey("legal_documents.id"))
    
    content = Column(Text) 
    hierarchy = Column(ARRAY(String)) # PG Array for GraphRAG
    token_count = Column(Integer)
    
    document = relationship("LegalDocument", back_populates="chunks")
