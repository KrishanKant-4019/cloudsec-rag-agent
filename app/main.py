from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import timedelta

from app.agent import run_agent
from app.database import User, get_db, init_db
from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token,
)

app = FastAPI(title="CloudSec RAG Agent")

# Initialize database on startup
init_db()


class AttachmentRequest(BaseModel):
    name: str
    mime_type: Optional[str] = None
    size_bytes: int = 0
    kind: Optional[str] = None
    text_content: Optional[str] = None


class QueryRequest(BaseModel):
    query: str = ""
    attachments: Optional[List[AttachmentRequest]] = None


class SignupRequest(BaseModel):
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_email: str


@app.get("/")
def read_root():
    return {"message": "CloudSec AI Agent is running 🚀"}


@app.post("/signup", response_model=dict)
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate password length
    if len(request.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters"
        )
    
    # Create new user
    hashed_pwd = hash_password(request.password)
    new_user = User(email=request.email, hashed_password=hashed_pwd)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "message": "User registered successfully",
        "user_id": new_user.id,
        "email": new_user.email
    }


@app.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return JWT token."""
    # Find user by email
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user.email})
    
    return TokenResponse(
        access_token=access_token,
        user_email=user.email
    )



@app.post("/ask")
def ask_agent(request: QueryRequest):
    try:
        response = run_agent(
            request.query,
            [attachment.dict() for attachment in (request.attachments or [])],
        )

        return {
            "answer": response
        }

    except Exception as e:
        return {"error": str(e)}
