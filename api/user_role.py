from typing import List
from fastapi import APIRouter, Depends

from controllers.user_role import user_role_controller
from models.user import User
from schemas.rbac import UserRoleRequest, UserRoleResponse, UserWithRolesResponse
from utils.auto_log import AutoLogger
from utils.common import ResponseSchema
from utils.rbac import get_current_superuser_or_permission
from utils.smart_log import with_auto_log, create_smart_logger_dep

router = APIRouter()


@router.post("/{user_id}/roles", summary="为用户分配角色", response_model=ResponseSchema[List[UserRoleResponse]])
@with_auto_log("user_role")
async def assign_user_roles(
    user_id: int,
    role_request: UserRoleRequest,
    current_user: User = Depends(get_current_superuser_or_permission("user", "manage")),
    auto_logger: AutoLogger = Depends(create_smart_logger_dep("user_role"))
):
    user_roles = await user_role_controller.assign_roles_to_user(user_id, role_request)
    return ResponseSchema(
        data=[UserRoleResponse.model_validate(ur) for ur in user_roles],
        message="角色分配成功"
    )


@router.get("/{user_id}/roles", summary="获取用户角色", response_model=ResponseSchema[List[UserRoleResponse]])
async def get_user_roles(
    user_id: int,
    current_user: User = Depends(get_current_superuser_or_permission("user", "read"))
):
    user_roles = await user_role_controller.get_user_roles(user_id)
    return ResponseSchema(
        data=[UserRoleResponse.model_validate(ur) for ur in user_roles]
    )


@router.delete("/{user_id}/roles/{role_id}", summary="移除用户角色", response_model=ResponseSchema[bool])
@with_auto_log("user_role")
async def remove_user_role(
    user_id: int,
    role_id: int,
    current_user: User = Depends(get_current_superuser_or_permission("user", "manage")),
    auto_logger: AutoLogger = Depends(create_smart_logger_dep("user_role"))
):
    result = await user_role_controller.remove_user_role(user_id, role_id)
    return ResponseSchema(data=result)


@router.get("/{user_id}/permissions", summary="获取用户完整权限信息", response_model=ResponseSchema[UserWithRolesResponse])
async def get_user_with_roles_and_permissions(
    user_id: int,
    current_user: User = Depends(get_current_superuser_or_permission("user", "read"))
):
    result = await user_role_controller.get_user_with_roles_and_permissions(user_id)
    
    response_data = UserWithRolesResponse(
        id=result["user"].id,
        username=result["user"].username,
        nickname=result["user"].nickname,
        is_active=result["user"].is_active,
        is_staff=result["user"].is_staff,
        is_superuser=result["user"].is_superuser,
        roles=result["roles"],
        permissions=result["permissions"]
    )
    
    return ResponseSchema(data=response_data)