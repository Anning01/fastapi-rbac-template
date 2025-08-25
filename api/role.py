from fastapi import APIRouter, Depends

from controllers.role import role_controller
from models.role import Role
from models.user import User
from schemas.page import QueryParams, get_list_params
from schemas.rbac import RoleCreate, RoleUpdate, RoleResponse
from utils.auto_log import AutoLogger
from utils.common import ResponseSchema, PaginationResponse
from utils.rbac import get_current_superuser_or_permission
from utils.smart_log import with_auto_log, create_smart_logger_dep

router = APIRouter()


@router.post("/", summary="创建角色", response_model=ResponseSchema[RoleResponse])
@with_auto_log("role")
async def create_role(
    role_create: RoleCreate,
    current_user: User = Depends(get_current_superuser_or_permission("role", "create")),
    auto_logger: AutoLogger = Depends(create_smart_logger_dep("role"))
):
    role = await role_controller.create_role(role_create)
    return ResponseSchema(data=role)


@router.get("/", summary="获取角色列表", response_model=ResponseSchema[PaginationResponse[RoleResponse]])
async def list_roles(
    params: QueryParams = Depends(get_list_params),
    current_user: User = Depends(get_current_superuser_or_permission("role", "read"))
):
    base_query = Role.all().prefetch_related('permissions')
    roles = await role_controller.list(params, RoleResponse, base_query=base_query)
    return ResponseSchema(data=roles)


@router.get("/{role_id}", summary="获取角色详情", response_model=ResponseSchema[RoleResponse])
async def get_role(
    role_id: int,
    current_user: User = Depends(get_current_superuser_or_permission("role", "read"))
):
    role = await role_controller.get_role_with_permissions(role_id)
    return ResponseSchema(data=role)


@router.put("/{role_id}", summary="更新角色", response_model=ResponseSchema[RoleResponse])
@with_auto_log("role")
async def update_role(
    role_id: int,
    role_update: RoleUpdate,
    current_user: User = Depends(get_current_superuser_or_permission("role", "update")),
    auto_logger: AutoLogger = Depends(create_smart_logger_dep("role"))
):
    role = await role_controller.update_role(role_id, role_update)
    return ResponseSchema(data=role)


@router.delete("/{role_id}", summary="删除角色", response_model=ResponseSchema[bool])
@with_auto_log("role")
async def delete_role(
    role_id: int,
    current_user: User = Depends(get_current_superuser_or_permission("role", "delete")),
    auto_logger: AutoLogger = Depends(create_smart_logger_dep("role"))
):
    result = await role_controller.delete_role(role_id)
    return ResponseSchema(data=result)