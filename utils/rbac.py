from functools import wraps
from typing import List, Union, Callable
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer

from core.deps import get_current_active_user
from models.user import User

security = HTTPBearer()


def require_permissions(resource: str, action: str):
    """
    权限装饰器 - 要求用户具有指定资源的指定操作权限
    
    Args:
        resource: 资源名称，如 'user', 'role', 'permission'
        action: 操作类型，如 'create', 'read', 'update', 'delete'
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 从kwargs中获取current_user，如果没有则从依赖注入中获取
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(status_code=500, detail="缺少用户认证信息")
            
            # 检查权限
            if not await current_user.has_permission(resource, action):
                raise HTTPException(
                    status_code=403, 
                    detail=f"权限不足: 需要 {resource}:{action} 权限"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_roles(roles: Union[str, List[str]]):
    """
    角色装饰器 - 要求用户具有指定角色之一
    
    Args:
        roles: 角色代码或角色代码列表
    """
    if isinstance(roles, str):
        roles = [roles]
    
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 从kwargs中获取current_user
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(status_code=500, detail="缺少用户认证信息")
            
            # 检查角色
            has_role = False
            for role_code in roles:
                if await current_user.has_role(role_code):
                    has_role = True
                    break
            
            if not has_role:
                raise HTTPException(
                    status_code=403, 
                    detail=f"权限不足: 需要以下角色之一 {', '.join(roles)}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_superuser(func: Callable):
    """超级用户装饰器 - 要求用户是超级用户"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        current_user = kwargs.get('current_user')
        if not current_user:
            raise HTTPException(status_code=500, detail="缺少用户认证信息")
        
        if not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="权限不足: 需要超级用户权限")
        
        return await func(*args, **kwargs)
    return wrapper


# 权限依赖注入函数
def get_current_user_with_permission(resource: str, action: str):
    """获取具有指定权限的当前用户"""
    async def permission_checker(current_user: User = Depends(get_current_active_user)):
        if not await current_user.has_permission(resource, action):
            raise HTTPException(
                status_code=403, 
                detail=f"权限不足: 需要 {resource}:{action} 权限"
            )
        return current_user
    return permission_checker


def get_current_user_with_role(role_code: str):
    """获取具有指定角色的当前用户"""
    async def role_checker(current_user: User = Depends(get_current_active_user)):
        if not await current_user.has_role(role_code):
            raise HTTPException(
                status_code=403, 
                detail=f"权限不足: 需要 {role_code} 角色"
            )
        return current_user
    return role_checker


def get_current_superuser_or_permission(resource: str, action: str):
    """获取超级用户或具有指定权限的用户"""
    async def checker(current_user: User = Depends(get_current_active_user)):
        if not current_user.is_superuser and not await current_user.has_permission(resource, action):
            raise HTTPException(
                status_code=403, 
                detail=f"权限不足: 需要超级用户权限或 {resource}:{action} 权限"
            )
        return current_user
    return checker


# 常用权限组合
def require_user_management():
    """用户管理权限"""
    return require_permissions("user", "manage")


def require_role_management():
    """角色管理权限"""
    return require_permissions("role", "manage")


def require_permission_management():
    """权限管理权限"""
    return require_permissions("permission", "manage")


def require_system_admin():
    """系统管理员权限"""
    return require_roles(["system_admin", "super_admin"])

