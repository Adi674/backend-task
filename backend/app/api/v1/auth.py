from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user import UserRegister, UserLogin, UserResponse
from app.models.user import User, UserRole
from app.core.security import hash_password, verify_password, create_access_token
from app.core.response import success_response, error_response
from app.core.dependencies import get_current_user

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)):

    # Check duplicate email
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        return error_response(
            message="Email already registered",
            status_code=status.HTTP_409_CONFLICT
        )

    # Role is ALWAYS user — hardcoded, not from request
    new_user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=UserRole.user        # ← hardcoded, never from payload
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return success_response(
        message="User registered successfully",
        data=UserResponse.model_validate(new_user).model_dump(mode="json"),
        status_code=status.HTTP_201_CREATED
    )


# Unified login for both user and admin
@router.post("/login")
def login(payload: UserLogin, db: Session = Depends(get_db)):

    # Find user by email
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        return error_response(
            message="Invalid email or password",
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    # Verify password
    if not verify_password(payload.password, user.hashed_password):
        return error_response(
            message="Invalid email or password",
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    # JWT carries the role — same endpoint, different access level
    access_token = create_access_token(data={
        "sub": str(user.id),
        "role": user.role.value,
        "email": user.email
    })

    return success_response(
        message="Login successful",
        data={
            "access_token": access_token,
            "token_type": "bearer",
            "role": user.role.value,        # frontend can redirect based on this
            "user": UserResponse.model_validate(user).model_dump(mode="json")
        }
    )


# Get current logged in user profile
@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return success_response(
        message="Profile fetched successfully",
        data=UserResponse.model_validate(current_user).model_dump(mode="json")
    )