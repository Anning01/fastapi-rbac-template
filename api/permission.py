from fastapi import APIRouter, Depends, HTTPException
from tortoise.exceptions import IntegrityError

from controllers.permission import permission_controller
from models.user import User
from schemas.page import QueryParams, get_list_params
from schemas.rbac import PermissionCreate, PermissionUpdate, PermissionResponse
from utils.auto_log import AutoLogger
from utils.common import ResponseSchema, PaginationResponse
from utils.rbac import get_current_superuser_or_permission
from utils.smart_log import with_auto_log, create_smart_logger_dep

router = APIRouter()


@router.post("/", summary="创建权限", response_model=ResponseSchema[PermissionResponse])
@with_auto_log("permission")
async def create_permission(
    permission_create: PermissionCreate,
    current_user: User = Depends(get_current_superuser_or_permission("permission", "create")),
    auto_logger: AutoLogger = Depends(create_smart_logger_dep("permission"))
):
    try:
        permission = await permission_controller.create(permission_create)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="权限名称、代码或资源-操作组合已存在")
    return ResponseSchema(data=permission)


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
    permission = await permission_controller.get(permission_id)
    return ResponseSchema(data=permission)


@router.put("/{permission_id}", summary="更新权限", response_model=ResponseSchema[PermissionResponse])
@with_auto_log("permission")
async def update_permission(
    permission_id: int,
    permission_update: PermissionUpdate,
    current_user: User = Depends(get_current_superuser_or_permission("permission", "update")),
    auto_logger: AutoLogger = Depends(create_smart_logger_dep("permission"))
):
    permission = await permission_controller.get(permission_id)
    instance = await permission_controller.update(permission, permission_update)
    return ResponseSchema(data=instance)


@router.delete("/{permission_id}", summary="删除权限", response_model=ResponseSchema[bool])
@with_auto_log("permission")
async def delete_permission(
    permission_id: int,
    current_user: User = Depends(get_current_superuser_or_permission("permission", "delete")),
    auto_logger: AutoLogger = Depends(create_smart_logger_dep("permission"))
):
    permission = await permission_controller.get(permission_id)
    result = await permission_controller.remove(permission)
    return ResponseSchema(data=result)