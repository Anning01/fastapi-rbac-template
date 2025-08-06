from fastapi import APIRouter, Depends

from controllers.rbac import permission_controller
from models.user import User
from schemas.page import QueryParams, get_list_params
from schemas.rbac import PermissionCreate, PermissionUpdate, PermissionResponse
from utils.common import ResponseSchema, PaginationResponse
from utils.rbac import get_current_superuser_or_permission

router = APIRouter()


@router.post("/", summary="创建权限", response_model=ResponseSchema[PermissionResponse])
async def create_permission(
    permission_create: PermissionCreate,
    current_user: User = Depends(get_current_superuser_or_permission("permission", "create"))
):
    permission = await permission_controller.create_permission(permission_create)
    return ResponseSchema(data=PermissionResponse.model_validate(permission))


@router.get("/", summary="获取权限列表", response_model=ResponseSchema[PaginationResponse[PermissionResponse]])
async def list_permissions(
    params: QueryParams = Depends(get_list_params),
    current_user: User = Depends(get_current_superuser_or_permission("permission", "read"))
):
    permissions = await permission_controller.list(params, PermissionResponse)
    return ResponseSchema(data=permissions)


@router.get("/{permission_id}", summary="获取权限详情", response_model=ResponseSchema[PermissionResponse])
async def get_permission(
    permission_id: int,
    current_user: User = Depends(get_current_superuser_or_permission("permission", "read"))
):
    permission = await permission_controller.get_permission(permission_id)
    return ResponseSchema(data=PermissionResponse.model_validate(permission))


@router.put("/{permission_id}", summary="更新权限", response_model=ResponseSchema[PermissionResponse])
async def update_permission(
    permission_id: int,
    permission_update: PermissionUpdate,
    current_user: User = Depends(get_current_superuser_or_permission("permission", "update"))
):
    permission = await permission_controller.update_permission(permission_id, permission_update)
    return ResponseSchema(data=PermissionResponse.model_validate(permission))


@router.delete("/{permission_id}", summary="删除权限", response_model=ResponseSchema[bool])
async def delete_permission(
    permission_id: int,
    current_user: User = Depends(get_current_superuser_or_permission("permission", "delete"))
):
    result = await permission_controller.delete_permission(permission_id)
    return ResponseSchema(data=result)