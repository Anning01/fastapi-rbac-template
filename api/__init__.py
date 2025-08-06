from fastapi import APIRouter

from api.auth import router as auth_router
from api.user import router as user_router
from api.role import router as role_router
from api.user_role import router as user_role_router
from api.permission import router as permission_router

api_router = APIRouter()


api_router.include_router(auth_router, prefix="/auth", tags=["身份校验"])
api_router.include_router(role_router, prefix="/role", tags=["角色管理"])
api_router.include_router(user_router, prefix="/user", tags=["用户管理"])
api_router.include_router(user_role_router, prefix="/user_role", tags=["用户角色管理"])
api_router.include_router(permission_router, prefix="/permission", tags=["权限管理"])
