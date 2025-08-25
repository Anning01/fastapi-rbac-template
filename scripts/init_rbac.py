"""初始化RBAC系统的默认权限和角色"""

import sys
import os

# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 项目根目录（假设 scripts 文件夹的父目录就是根目录）
project_root = os.path.dirname(current_dir)
# 将根目录加入 Python 路径
sys.path.append(project_root)

from config import settings
from models.role import Permission, Role
from models.user import User


async def init_permissions():
    """初始化默认权限"""
    default_permissions = [
        # 用户管理权限
        {"name": "创建用户", "code": "user:create", "resource": "user", "action": "create", "description": "创建新用户"},
        {"name": "查看用户", "code": "user:read", "resource": "user", "action": "read", "description": "查看用户信息"},
        {"name": "更新用户", "code": "user:update", "resource": "user", "action": "update", "description": "更新用户信息"},
        {"name": "删除用户", "code": "user:delete", "resource": "user", "action": "delete", "description": "删除用户"},
        {"name": "管理用户", "code": "user:manage", "resource": "user", "action": "manage", "description": "用户管理权限"},
        
        # 角色管理权限
        {"name": "创建角色", "code": "role:create", "resource": "role", "action": "create", "description": "创建新角色"},
        {"name": "查看角色", "code": "role:read", "resource": "role", "action": "read", "description": "查看角色信息"},
        {"name": "更新角色", "code": "role:update", "resource": "role", "action": "update", "description": "更新角色信息"},
        {"name": "删除角色", "code": "role:delete", "resource": "role", "action": "delete", "description": "删除角色"},
        {"name": "管理角色", "code": "role:manage", "resource": "role", "action": "manage", "description": "角色管理权限"},
        
        # 权限管理权限
        {"name": "创建权限", "code": "permission:create", "resource": "permission", "action": "create", "description": "创建新权限"},
        {"name": "查看权限", "code": "permission:read", "resource": "permission", "action": "read", "description": "查看权限信息"},
        {"name": "更新权限", "code": "permission:update", "resource": "permission", "action": "update", "description": "更新权限信息"},
        {"name": "删除权限", "code": "permission:delete", "resource": "permission", "action": "delete", "description": "删除权限"},
        {"name": "管理权限", "code": "permission:manage", "resource": "permission", "action": "manage", "description": "权限管理权限"},
        
        # 系统管理权限
        {"name": "日志查看", "code": "operation_log:read", "resource": "operation_log", "action": "config", "description": "后台操作日志"},
    ]
    
    created_permissions = []
    for perm_data in default_permissions:
        permission, created = await Permission.get_or_create(
            code=perm_data["code"],
            defaults=perm_data
        )
        if created:
            created_permissions.append(permission)
            print(f"创建权限: {permission.name}")
    
    return created_permissions


async def init_roles():
    """初始化默认角色"""
    # 确保权限已存在
    await init_permissions()
    
    # 定义默认角色
    default_roles = [
        {
            "name": "系统管理员",
            "code": "system_admin",
            "description": "系统管理员，拥有所有权限",
            "permissions": ["user:manage", "role:manage", "permission:manage", "operation_log:read"]
        },
        {
            "name": "用户管理员",
            "code": "user_admin",
            "description": "用户管理员，负责用户管理",
            "permissions": ["user:create", "user:read", "user:update", "user:manage"]
        },
        {
            "name": "角色管理员",
            "code": "role_admin",
            "description": "角色管理员，负责角色和权限管理",
            "permissions": ["role:create", "role:read", "role:update", "role:manage", "permission:read"]
        },
        {
            "name": "只读用户",
            "code": "readonly_user",
            "description": "只读用户，只能查看信息",
            "permissions": ["user:read", "role:read", "permission:read"]
        },
        {
            "name": "普通管理员",
            "code": "admin",
            "description": "普通管理员，基本管理权限",
            "permissions": ["user:read", "user:update", "role:read"]
        }
    ]
    
    created_roles = []
    for role_data in default_roles:
        role, created = await Role.get_or_create(
            code=role_data["code"],
            defaults={
                "name": role_data["name"],
                "description": role_data["description"]
            }
        )
        
        if created:
            # 分配权限给角色
            permission_codes = role_data["permissions"]
            permissions = await Permission.filter(code__in=permission_codes)
            await role.permissions.add(*permissions)
            
            created_roles.append(role)
            print(f"创建角色: {role.name}, 权限数量: {len(permissions)}")
        else:
            print(f"角色已存在: {role.name}")
    
    return created_roles


async def create_admin_user():
    """创建默认管理员用户"""
    from utils.password import get_password_hash
    
    # 检查是否已存在超级用户
    superuser = await User.filter(is_superuser=True).first()
    if superuser:
        print(f"超级用户已存在: {superuser.username}")
        return superuser
    
    # 创建默认超级用户
    admin_user = await User.create(
        username="admin",
        password=get_password_hash("123456"),
        is_superuser=True,
        is_staff=True,
        is_active=True
    )
    
    print(f"创建超级用户: {admin_user.username}, 密码: 123456")
    return admin_user


async def init_rbac_system():
    """初始化整个RBAC系统"""
    print("开始初始化RBAC系统...")
    
    # 1. 初始化权限
    print("初始化权限...")
    await init_permissions()
    
    # 2. 初始化角色
    print("初始化角色...")
    await init_roles()
    
    # 3. 创建管理员用户
    print("创建管理员用户...")
    await create_admin_user()
    
    print("RBAC系统初始化完成!")


if __name__ == "__main__":
    import asyncio
    from tortoise import Tortoise

    async def main():
        # 这里需要根据你的数据库配置进行调整
        await Tortoise.init(
            db_url=settings.DATABASE_URL,  # 根据实际情况修改
            modules={"models": [f"models.{module}" for module in __import__("models").__all__]},
        )
        await Tortoise.generate_schemas()

        await init_rbac_system()

        await Tortoise.close_connections()

    asyncio.run(main())