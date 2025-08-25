from fastapi import HTTPException

from core.crud import CRUDBase
from models.role import Role, Permission, UserRole
from schemas.rbac import RoleCreate, RoleUpdate
from tortoise.exceptions import IntegrityError


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

    async def list_roles(self, skip: int = 0, limit: int = 100) -> list[Role]:
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


role_controller = RoleController()
