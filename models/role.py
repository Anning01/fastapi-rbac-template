from tortoise import fields

from models._base import AbstractBaseModel


class Permission(AbstractBaseModel):
    """权限模型"""
    name = fields.CharField(max_length=100, unique=True, description="权限名称")
    code = fields.CharField(max_length=100, unique=True, description="权限代码")
    description = fields.CharField(max_length=255, blank=True, null=True, description="权限描述")
    resource = fields.CharField(max_length=100, description="资源名称")
    action = fields.CharField(max_length=50, description="操作类型")

    class Meta:
        table = "permissions"
        unique_together = [("resource", "action")]

    def __str__(self):
        return f"{self.resource}:{self.action}"


class Role(AbstractBaseModel):
    """角色模型"""
    name = fields.CharField(max_length=100, unique=True, description="角色名称")
    code = fields.CharField(max_length=100, unique=True, description="角色代码")
    description = fields.CharField(max_length=255, blank=True, null=True, description="角色描述")
    is_active = fields.BooleanField(default=True, description="是否启用")
    
    # 多对多关系：角色拥有多个权限
    permissions = fields.ManyToManyField(
        "models.Permission",
        related_name="roles",
        through="role_permissions",
        description="角色权限"
    )

    class Meta:
        table = "roles"

    def __str__(self):
        return self.name


class UserRole(AbstractBaseModel):
    """用户角色关联模型"""
    user = fields.ForeignKeyField("models.User", related_name="user_roles", description="用户")
    role = fields.ForeignKeyField("models.Role", related_name="role_users", description="角色")
    is_active = fields.BooleanField(default=True, description="是否启用")

    class Meta:
        table = "user_roles"
        unique_together = [("user", "role")]

    def __str__(self):
        return f"{self.user.username} - {self.role.name}"