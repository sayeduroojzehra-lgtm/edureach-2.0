from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.user import UserRegister, UserLogin, UserResponse, TokenResponse, ProfileUpdateRequest
from app.utils.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
)

router = APIRouter(prefix="/auth", tags=["Authentication & Profiles"])

@router.post("/login", response_model=TokenResponse, summary="Login or auto-enroll user")
def login(payload: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate a student or teacher.
    If the email is not registered yet (prototype mode), it seamlessly creates
    the account using the provided details and logs them in immediately.
    """
    user = db.query(User).filter(User.email == payload.email.lower()).first()

    if not user:
        # Auto-create for seamless prototype experience if name/role provided
        user_name = payload.name if payload.name else payload.email.split("@")[0].title()
        user_role = payload.role if payload.role else UserRole.STUDENT
        user_std = payload.standard if payload.standard else 8
        
        user = User(
            name=user_name,
            email=payload.email.lower(),
            hashed_password=get_password_hash(payload.password),
            role=user_role,
            standard=user_std if user_role == UserRole.STUDENT else None
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # Validate password if user exists
        if not verify_password(payload.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

    token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED, summary="Register new user")
def register(payload: UserRegister, db: Session = Depends(get_db)):
    """Explicitly register a new student or teacher."""
    existing = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email is already registered."
        )

    user = User(
        name=payload.name,
        email=payload.email.lower(),
        hashed_password=get_password_hash(payload.password),
        role=payload.role,
        standard=payload.standard if payload.role == UserRole.STUDENT else None
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )

@router.get("/me", response_model=UserResponse, summary="Get current logged-in user")
def get_me(current_user: User = Depends(get_current_user)):
    """Return the profile information of the currently authenticated user."""
    return UserResponse.model_validate(current_user)

@router.put("/profile", response_model=UserResponse, summary="Update user profile")
def update_profile(
    payload: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update name or standard for the current user."""
    if payload.name is not None:
        current_user.name = payload.name
    if payload.standard is not None and current_user.role == UserRole.STUDENT:
        current_user.standard = payload.standard
    db.commit()
    db.refresh(current_user)
    return UserResponse.model_validate(current_user)
