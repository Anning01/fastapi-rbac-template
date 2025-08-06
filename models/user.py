from tortoise import fields

from models._base import AbstractBaseModel


class User(AbstractBaseModel):
    """用户表"""
    nickname = fields.CharField(max_length=50, blank=True, null=True, description="昵称")
    avatar = fields.CharField(max_length=100, blank=True, null=True, description="头像")
    username = fields.CharField(max_length=50, unique=True, description="用户名")
    password = fields.CharField(max_length=255, blank=True, null=True, description="密码")
    is_active = fields.BooleanField(default=True, description="是否允许登录")
    is_staff = fields.BooleanField(default=False, description="是否在职(登录后台)")
    is_superuser = fields.BooleanField(default=False, description="超级管理员")
    last_login = fields.DatetimeField(blank=True, null=True, description="最后登录时间")

    class Meta:
        table = "users"

    def __str__(self):
        return self.username

    async def get_permissions(self):
        """获取用户所有权限"""
        if self.is_superuser:
            from models.role import Permission
            return await Permission.all()
        
        permissions = []
        user_roles = await self.user_roles.filter(is_active=True).prefetch_related('role__permissions')
        for user_role in user_roles:
            if user_role.role.is_active:
                role_permissions = await user_role.role.permissions.all()
                permissions.extend(role_permissions)
        
        # 去重
        return list({perm.id: perm for perm in permissions}.values())

    async def has_permission(self, resource: str, action: str) -> bool:
        """检查用户是否有指定权限"""
        if self.is_superuser:
            return True
        
        permissions = await self.get_permissions()
        return any(perm.resource == resource and perm.action == action for perm in permissions)

    async def has_role(self, role_code: str) -> bool:
        """检查用户是否有指定角色"""
        if self.is_superuser:
            return True
        
        user_roles = await self.user_roles.filter(is_active=True).prefetch_related('role')
        return any(user_role.role.code == role_code and user_role.role.is_active for user_role in user_roles)
