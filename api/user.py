from fastapi import APIRouter, Depends, HTTPException

from controllers.user import user_controller
from core.deps import get_current_active_user
from models.user import User
from schemas.auth import UserResponse, UserCreate
from schemas.page import QueryParams, get_list_params
from utils.common import PaginationResponse, ResponseSchema
from utils.rbac import get_current_superuser_or_permission

router = APIRouter()


@router.get("/info", summary="获取用户信息", response_model=ResponseSchema[UserResponse])
async def get_user_info(current_user: User = Depends(get_current_active_user)):
    return ResponseSchema(data=current_user)


@router.post("/create", summary="创建用户", response_model=ResponseSchema[UserResponse])
async def create_user(
    user_create: UserCreate,
    current_user: User = Depends(get_current_superuser_or_permission("user", "create"))
):
    user = await user_controller.create_user(user_create)
    return ResponseSchema(data=user)


@router.get("/list", summary="获取用户列表", response_model=ResponseSchema[PaginationResponse[UserResponse]])
async def list_users(
    params: QueryParams = Depends(get_list_params),
    current_user: User = Depends(get_current_superuser_or_permission("user", "read"))
):
    # json内搜索使用.语法，并且完全匹配
    search_fields: list[str] = [
        "nickname", "user_extra.name"
    ]

    users = await user_controller.list(params, UserResponse, search_fields)
    return ResponseSchema(data=users)


@router.get("/{user_id}", summary="获取用户详情", response_model=ResponseSchema[UserResponse])
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_superuser_or_permission("user", "read"))
):
    user = await user_controller.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return ResponseSchema(data=user)


@router.put("/{user_id}/activate", summary="激活用户", response_model=ResponseSchema[bool])
async def activate_user(
    user_id: int,
    current_user: User = Depends(get_current_superuser_or_permission("user", "manage"))
):
    user = await user_controller.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    user.is_active = True
    await user.save()
    return ResponseSchema(data=True)


@router.put("/{user_id}/deactivate", summary="禁用用户", response_model=ResponseSchema[bool])
async def deactivate_user(
    user_id: int,
    current_user: User = Depends(get_current_superuser_or_permission("user", "manage"))
):
    user = await user_controller.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    if user.is_superuser:
        raise HTTPException(status_code=400, detail="不能禁用超级用户")
    
    user.is_active = False
    await user.save()
    return ResponseSchema(data=True)

