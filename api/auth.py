from datetime import timedelta, datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from config import settings
from controllers.user import user_controller
from models.user import User
from schemas.auth import Token, JWTPayload
from utils.common import ResponseSchema
from utils.jwt_utils import TokenType, verify_token

router = APIRouter()


@router.post("/login", summary="后台登录登录", response_model=ResponseSchema[Token])
async def login(login_data: OAuth2PasswordRequestForm = Depends()):
    user: User = await user_controller.authenticate(
        username=login_data.username, 
        password=login_data.password
    )
    await user_controller.update_last_login(user)
    login_timestamp = int(user.last_login.timestamp())
    expire = datetime.utcnow() + timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS)
    access_token = user_controller.create_token(
        token_type=TokenType.ACCESS,
        data=JWTPayload(user_id=user.id, username=user.username, is_superuser=user.is_superuser, login_time=login_timestamp))
    refresh_token = user_controller.create_token(
        token_type=TokenType.REFRESH,
        data=JWTPayload(user_id=user.id, username=user.username, is_superuser=user.is_superuser, login_time=login_timestamp))
    return ResponseSchema(data=Token(access_token=access_token, refresh_token=refresh_token, expire=int(expire.timestamp())))



@router.post("/refresh", summary="刷新token", response_model=ResponseSchema[Token])
async def refresh(refresh_token: str):

    payload = verify_token(refresh_token, TokenType.REFRESH)
    user_id = payload.user_id
    user = await User.filter(id=user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    expire = datetime.utcnow() + timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS)

    await user_controller.update_last_login(user)
    login_timestamp = int(user.last_login.timestamp())
    access_token = user_controller.create_token(
        token_type=TokenType.ACCESS,
        data=JWTPayload(user_id=user.id, username=user.username, is_superuser=user.is_superuser, login_time=login_timestamp))
    refresh_token = user_controller.create_token(
        token_type=TokenType.REFRESH,
        data=JWTPayload(user_id=user.id, username=user.username, is_superuser=user.is_superuser, login_time=login_timestamp))

    return ResponseSchema(data=Token(access_token=access_token, refresh_token=refresh_token, expire=int(expire.timestamp())))

