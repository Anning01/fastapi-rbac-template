from datetime import datetime
from typing import Optional
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi import Request, HTTPException
from fastapi.security import OAuth2
from pydantic import BaseModel, Field
from fastapi.security.utils import get_authorization_scheme_param
from starlette import status

class UserCreate(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")
    is_superuser: bool = Field(default=False, description="是否为超级管理员")


class UserUpdate(BaseModel):
    nickname: Optional[str] = Field(None, description="昵称")
    avatar: Optional[str] = Field(None, description="头像")

class JWTPayload(BaseModel):
    user_id: int
    username: str
    is_superuser: bool
    login_time: int


class JWTDecoder(JWTPayload):
    type: str
    exp: int

class Token(BaseModel):
    access_token: str
    refresh_token: str
    expire: int
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: int = Field(..., description="用户ID")
    username: Optional[str] = Field(None, description="用户名")
    nickname: Optional[str] = Field(None, description="昵称")
    avatar: Optional[str] = Field(None, description="头像")
    is_superuser: bool = Field(default=False, description="是否为超级管理员")
    is_active: bool = Field(default=True, description="是否激活")
    is_staff: bool = Field(default=False, description="是否在职(登录后台)")
    last_login: Optional[datetime] = Field(None, description="最后登录时间")

    class Config:
        from_attributes = True

