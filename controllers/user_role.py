from typing import List

from fastapi import HTTPException

from core.crud import CRUDBase
from models.role import Role, UserRole
from models.user import User
from schemas.rbac import (
    UserRoleRequest
)


class UserRoleController(CRUDBase[UserRole, None, None]):

    def __init__(self):
        super().__init__(model=UserRole)

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
        
        return await UserRole.filter(user_id=user_id).prefetch_related('role', 'role__permissions')

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


user_role_controller = UserRoleController()