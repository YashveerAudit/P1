"""Registration, login and current-user endpoints."""
from fastapi import APIRouter, status

from app.api.dependencies import AuthServiceDep, CurrentUser
from app.schemas.user import TokenResponse, UserLogin, UserRegister, UserResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"description": "Email already registered"}},
)
async def register(payload: UserRegister, service: AuthServiceDep):
    user = await service.register(payload)
    return TokenResponse(access_token=service.issue_token(user), user=UserResponse.model_validate(user))


@router.post(
    "/login",
    response_model=TokenResponse,
    responses={401: {"description": "Incorrect email or password"}},
)
async def login(payload: UserLogin, service: AuthServiceDep):
    user = await service.login(payload)
    return TokenResponse(access_token=service.issue_token(user), user=UserResponse.model_validate(user))


@router.get("/me", response_model=UserResponse, responses={401: {"description": "Not signed in"}})
async def me(user: CurrentUser):
    return user
