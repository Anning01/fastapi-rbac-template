from typing import List

from fastapi import HTTPException
from tortoise.exceptions import IntegrityError

from core.crud import CRUDBase
from models.role import Role, Permission, UserRole
from models.user import User
from schemas.rbac import (
    RoleCreate, RoleUpdate, PermissionCreate, PermissionUpdate,
    UserRoleRequest
)


class RoleController(CRUDBase[Role, RoleCreate, RoleUpdate]):
    def __init__(self):
        super().__init__(model=Role)

    async def create_role(self, obj_in: RoleCreate) -> Role:
        try:
            role_data = obj_in.model_dump(exclude={'permission_ids'})
            role = await self.create(role_data)
            
            if obj_in.permission_ids:
                permissions = await Permission.filter(id__in=obj_in.permission_ids)
                await role.permissions.add(*permissions)
            
            return await Role.get(id=role.id).prefetch_related('permissions')
        except IntegrityError:
            raise HTTPException(status_code=400, detail="角色名称或代码已存在")

    async def update_role(self, role_id: int, obj_in: RoleUpdate) -> Role:
        role = await Role.get_or_none(id=role_id)
        if not role:
            raise HTTPException(status_code=404, detail="角色不存在")
        
        update_data = obj_in.model_dump(exclude_unset=True, exclude={'permission_ids'})
        if update_data:
            await role.update_from_dict(update_data)
            await role.save()
        
        if obj_in.permission_ids is not None:
            await role.permissions.clear()
            if obj_in.permission_ids:
                permissions = await Permission.filter(id__in=obj_in.permission_ids)
                await role.permissions.add(*permissions)
        
        return await Role.get(id=role_id).prefetch_related('permissions')

    async def get_role_with_permissions(self, role_id: int) -> Role:
        role = await Role.get_or_none(id=role_id).prefetch_related('permissions')
        if not role:
            raise HTTPException(status_code=404, detail="角色不存在")
        return role

    async def list_roles(self, skip: int = 0, limit: int = 100) -> List[Role]:
        return await Role.all().prefetch_related('permissions').offset(skip).limit(limit)

    async def delete_role(self, role_id: int) -> bool:
        role = await Role.get_or_none(id=role_id)
        if not role:
            raise HTTPException(status_code=404, detail="角色不存在")
        
        # 检查是否有用户使用此角色
        user_count = await UserRole.filter(role_id=role_id, is_active=True).count()
        if user_count > 0:
            raise HTTPException(status_code=400, detail="该角色正在被使用，无法删除")
        
        await role.delete()
        return True


class PermissionController(CRUDBase[Permission, PermissionCreate, PermissionUpdate]):
    def __init__(self):
        super().__init__(model=Permission)



class UserRoleController:
    async def assign_roles_to_user(self, user_id: int, role_request: UserRoleRequest) -> List[UserRole]:
        user = await User.get_or_none(id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 验证角色是否存在
        roles = await Role.filter(id__in=role_request.role_ids, is_active=True)
        if len(roles) != len(role_request.role_ids):
            raise HTTPException(status_code=400, detail="部分角色不存在或已禁用")
        
        # 清除用户现有角色
        await UserRole.filter(user_id=user_id).delete()
        
        # 分配新角色
        user_roles = []
        for role_id in role_request.role_ids:
            user_role = await UserRole.create(user_id=user_id, role_id=role_id)
            user_roles.append(user_role)
        
        return await UserRole.filter(user_id=user_id).prefetch_related('role')

    async def get_user_roles(self, user_id: int) -> List[UserRole]:
        user = await User.get_or_none(id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        return await UserRole.filter(user_id=user_id, is_active=True).prefetch_related('role__permissions')

    async def remove_user_role(self, user_id: int, role_id: int) -> bool:
        user_role = await UserRole.get_or_none(user_id=user_id, role_id=role_id)
        if not user_role:
            raise HTTPException(status_code=404, detail="用户角色关联不存在")
        
        await user_role.delete()
        return True

    async def get_user_with_roles_and_permissions(self, user_id: int) -> dict:
        user = await User.get_or_none(id=user_id).prefetch_related('user_roles__role__permissions')
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        roles = []
        all_permissions = []
        
        for user_role in user.user_roles:
            if user_role.is_active and user_role.role.is_active:
                roles.append(user_role.role)
                permissions = await user_role.role.permissions.all()
                all_permissions.extend(permissions)
        
        # 去重权限
        unique_permissions = list({perm.id: perm for perm in all_permissions}.values())
        
        return {
            "user": user,
            "roles": roles,
            "permissions": unique_permissions
        }


role_controller = RoleController()
permission_controller = PermissionController()
user_role_controller = UserRoleController()