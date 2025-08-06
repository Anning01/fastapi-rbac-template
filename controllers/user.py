from datetime import datetime
from typing import Optional

from fastapi.exceptions import HTTPException

from core.crud import CRUDBase
from models.user import User
from schemas.auth import UserCreate, UserUpdate, JWTPayload
from utils.jwt_utils import create_access_token, TokenType
from utils.password import get_password_hash, verify_password


class UserController(CRUDBase[User, UserCreate, UserUpdate]):
    def __init__(self):
        super().__init__(model=User)

    async def get_by_username(self, username: str) -> Optional[User]:
        return await self.model.filter(username=username).first()

    async def create_user(self, obj_in: UserCreate) -> User:
        obj_in.password = get_password_hash(password=obj_in.password)
        obj = await self.create(obj_in)
        return obj

    async def update_last_login(self, user: User) -> None:
        user.last_login = datetime.now()
        await user.save()

    async def authenticate(self, username: str, password: str) -> Optional[User]:
        user = await self.get_by_username(username)
        if not user:
            raise HTTPException(status_code=400, detail="用户名不存在")
        verified = verify_password(password, user.password)
        if not verified:
            raise HTTPException(status_code=400, detail="密码错误!")
        if not user.is_active:
            raise HTTPException(status_code=400, detail="用户已被禁用")
        if not user.is_staff:
            raise HTTPException(status_code=400, detail="用户不允许登录后台")
        return user

    async def reset_password(self, user: User, password: str) -> None:
        if user.is_superuser:
            raise HTTPException(status_code=403, detail="不允许重置超级管理员密码")
        user.password = get_password_hash(password=password)
        await user.save()

    def create_token(self, token_type: TokenType, data: JWTPayload) -> str:
        return create_access_token(
            token_type=token_type,
            data=data,
        )


user_controller = UserController()
