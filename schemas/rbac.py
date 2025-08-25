from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class PermissionBase(BaseModel):
    name: str = Field(..., description="权限名称")
    code: str = Field(..., description="权限代码")
    description: Optional[str] = Field(None, description="权限描述")
    resource: str = Field(..., description="资源名称")
    action: str = Field(..., description="操作类型")


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(BaseModel):
    name: Optional[str] = Field(None, description="权限名称")
    description: Optional[str] = Field(None, description="权限描述")


class PermissionResponse(PermissionBase):
    id: int = Field(..., description="权限ID")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        from_attributes = True


class RoleBase(BaseModel):
    name: str = Field(..., description="角色名称")
    code: str = Field(..., description="角色代码")
    description: Optional[str] = Field(None, description="角色描述")
    is_active: bool = Field(True, description="是否启用")


class RoleCreate(RoleBase):
    permission_ids: List[int] = Field(default=[], description="权限ID列表")


class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, description="角色名称")
    description: Optional[str] = Field(None, description="角色描述")
    is_active: Optional[bool] = Field(None, description="是否启用")
    permission_ids: Optional[List[int]] = Field(None, description="权限ID列表")


class RoleResponse(RoleBase):
    id: int = Field(..., description="角色ID")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    permissions: List[PermissionResponse] = Field(default=[], description="角色权限")

    class Config:
        from_attributes = True


class UserRoleRequest(BaseModel):
    role_ids: List[int] = Field(..., description="角色ID列表")


class UserRoleResponse(BaseModel):
    id: int = Field(..., description="用户角色关联ID")
    user_id: int = Field(..., description="用户ID")
    role: RoleResponse = Field(..., description="角色信息")
    is_active: bool = Field(..., description="是否启用")
    created_at: Optional[datetime] = Field(None, description="创建时间")

    class Config:
        from_attributes = True


class UserWithRolesResponse(BaseModel):
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    nickname: Optional[str] = Field(None, description="昵称")
    is_active: bool = Field(..., description="是否激活")
    is_staff: bool = Field(..., description="是否在职")
    is_superuser: bool = Field(..., description="是否超级用户")
    roles: List[RoleResponse] = Field(default=[], description="用户角色")
    permissions: List[PermissionResponse] = Field(default=[], description="用户权限")

    class Config:
        from_attributes = True