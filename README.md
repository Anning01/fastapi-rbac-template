# FastAPI RBAC 权限管理模板

[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116.1+-green.svg)](https://fastapi.tiangolo.com)
[![Tortoise ORM](https://img.shields.io/badge/Tortoise%20ORM-0.25.1+-orange.svg)](https://tortoise.github.io)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

基于 FastAPI + Tortoise ORM + JWT 的 RBAC（基于角色的访问控制）权限管理系统模板，帮助快速构建具备完整权限管理功能的后台系统。

## ✨ 特性

- 🔐 **完整的 RBAC 权限系统**：用户-角色-权限三层权限控制
- 🚀 **基于 FastAPI**：现代、快速的 Python Web 框架
- 📊 **Tortoise ORM**：异步 Python ORM，性能优异
- 🔑 **JWT 认证**：安全的无状态身份认证
- 📝 **自动 API 文档**：Swagger/OpenAPI 自动生成
- 🎯 **装饰器权限控制**：简洁易用的权限验证
- 🔧 **完整的 CRUD 操作**：用户、角色、权限管理
- 🏗️ **模块化设计**：清晰的项目结构
- ⚡ **Redis 支持**：缓存和会话管理
- 🐳 **Docker 支持**：容器化部署

## 📁 项目结构

```
rbac-template/
├── api/                    # API路由
│   ├── __init__.py
│   ├── auth.py            # 认证相关接口
│   ├── user.py            # 用户管理接口
│   ├── role.py            # 角色管理接口
│   ├── permission.py      # 权限管理接口
│   ├── operation_log.py   # 操作日志接口
│   └── user_role.py       # 用户角色管理接口
├── models/                 # 数据模型
│   ├── _base.py           # 基础模型
│   ├── user.py            # 用户模型
│   ├── operation_log.py   # 操作日志模型
│   └── role.py            # 角色权限模型
├── schemas/               # 数据验证模式
│   ├── auth.py            # 认证相关模式
│   ├── rbac.py            # RBAC 相关模式
│   └── page.py            # 分页模式
├── utils/                 # 工具函数
│   ├── rbac.py            # RBAC 权限装饰器
│   ├── jwt_utils.py       # JWT 工具
│   ├── password.py        # 密码工具
│   └── common.py          # 通用工具
├── core/                  # 核心模块
│   ├── crud.py            # CRUD 基础类
│   ├── deps.py            # 依赖注入
│   └── redis_manager.py   # Redis 管理
├── controllers/           # 控制器层
│   ├── permission.py      # 权限控制器
│   ├── role.py            # 角色控制器
│   ├── user_role.py       # 用户角色控制器
│   ├── operation_log.py   # 操作日志控制器
│   └── user.py            # 用户控制器
├── scripts/               # 脚本
│   └── init_rbac.py       # RBAC 初始化脚本
├── config.py              # 配置文件
├── main.py                # 应用入口
├── pyproject.toml         # 项目配置
└── Makefile              # 构建脚本
```

## 🛠️ 技术栈

- **Web 框架**: FastAPI 0.116.1+
- **数据库 ORM**: Tortoise ORM 0.25.1+
- **数据库**: PostgreSQL (支持 AsyncPG)
- **身份认证**: JWT (PyJWT)
- **密码加密**: Passlib + Argon2
- **缓存**: Redis 6.3.0+
- **ASGI 服务器**: Uvicorn
- **包管理**: UV (推荐) 或 pip

## 🚀 快速开始

### 环境要求

- Python 3.12+
- PostgreSQL 12+
- Redis 6.0+

### 1. 克隆项目

```bash
git clone https://github.com/Anning01/fastapi-rbac-template.git
cd fastapi-rbac-template
```

### 2. 安装依赖

使用 UV (推荐):
```bash
# 安装 UV
pip install uv

# 安装依赖
uv sync
```

或使用 pip:
```bash
pip install -r requirements.txt
```

### 3. 环境配置

创建 `.env` 文件：
```bash
cp .env.example .env
```

编辑 `.env` 文件配置数据库等信息：
```env
# 数据库配置
DATABASE_URL=postgres://username:password@localhost:5432/fastapi_db

# JWT 配置
SECRET_KEY=your-secret-key-here

# Redis 配置
REDIS_URL=redis://:@localhost:6379/0

# 应用配置
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

### 4. 数据库初始化

```bash
# 使用 UV
uv run python scripts/init_rbac.py

# 或使用 Python
python scripts/init_rbac.py
```

### 5. 启动应用

开发模式:
```bash
make dev
```

或直接使用 uvicorn:
```bash
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 6. 访问应用

- API 文档: http://localhost:8000/docs
- 备用文档: http://localhost:8000/redoc

## 🔧 核心功能

### RBAC 权限模型

本项目实现了完整的 RBAC (Role-Based Access Control) 权限控制：

- **用户 (User)**: 系统用户
- **角色 (Role)**: 权限的集合
- **权限 (Permission)**: 具体的操作权限
- **用户角色 (UserRole)**: 用户与角色的关联

### 权限控制

#### 1. 装饰器方式

```python
from utils.rbac import require_permissions, require_roles, require_superuser

# 要求特定权限
@require_permissions("user", "create")
async def create_user():
    pass

# 要求特定角色
@require_roles(["admin", "user_admin"])
async def manage_users():
    pass

# 要求超级用户
@require_superuser
async def system_config():
    pass
```

#### 2. 依赖注入方式

```python
from utils.rbac import get_current_user_with_permission

@app.post("/users")
async def create_user(
    current_user: User = Depends(get_current_user_with_permission("user", "create"))
):
    pass
```

#### 3. 程序化检查

```python
# 检查权限
has_perm = await user.has_permission("user", "create")

# 检查角色
has_role = await user.has_role("admin")
```

### API 接口

#### 认证接口 (/api/auth)
- `POST /login` - 用户登录
- `POST /refresh` - 刷新令牌
- `POST /logout` - 用户登出
- `GET /me` - 获取当前用户信息

#### 用户管理 (/api/user)
- `GET /users` - 获取用户列表
- `POST /users` - 创建用户
- `PUT /users/{id}` - 更新用户
- `DELETE /users/{id}` - 删除用户

#### 角色管理 (/api/role)
- `GET /roles` - 获取角色列表
- `POST /roles` - 创建角色
- `PUT /roles/{id}` - 更新角色
- `DELETE /roles/{id}` - 删除角色

#### 权限管理 (/api/permission)
- `GET /permission` - 获取权限列表
- `POST /permission` - 创建权限
- `PUT /permission/{id}` - 更新权限
- `DELETE /permission/{id}` - 删除权限

### 预设权限和角色

系统初始化时会创建以下默认权限和角色：

#### 默认权限
- 用户管理：`user:create`, `user:read`, `user:update`, `user:delete`, `user:manage`
- 角色管理：`role:create`, `role:read`, `role:update`, `role:delete`, `role:manage`
- 权限管理：`permission:create`, `permission:read`, `permission:update`, `permission:delete`, `permission:manage`
- 系统管理：`system:config`, `system:monitor`, `system:log`

#### 默认角色
- **系统管理员** (`system_admin`): 拥有所有权限
- **用户管理员** (`user_admin`): 用户管理权限
- **角色管理员** (`role_admin`): 角色和权限管理权限
- **只读用户** (`readonly_user`): 只读权限
- **普通管理员** (`admin`): 基本管理权限

#### 默认用户
- 用户名: `admin`
- 密码: `123456`
- 权限: 超级用户

## 🔨 开发指南

### Makefile 命令

```bash
make help           # 查看所有可用命令
make install        # 安装依赖
make install-dev    # 安装开发依赖
make dev            # 开发模式启动
make start          # 生产模式启动
make test           # 运行测试
make format         # 格式化代码
make lint           # 代码检查
make clean          # 清理临时文件
```

### 操作日志功能

系统内置了完整的操作日志功能，自动记录用户的重要操作：

#### 功能特点
- 🔍 **自动记录**：通过装饰器自动记录 API 操作
- 📝 **详细信息**：记录操作前后数据、IP、用户代理等
- 🎯 **灵活配置**：支持自定义日志记录策略
- 📊 **完整追踪**：支持用户、模块、操作类型等多维度查询

#### 使用方法

##### 1. 装饰器自动记录

```python
from utils.smart_log import with_auto_log, create_smart_logger_dep
from utils.auto_log import AutoLogger

@router.post("/users", summary="创建用户")
@with_auto_log("user")  # 指定操作模块
async def create_user(
    user_data: UserCreate,
    auto_logger: AutoLogger = Depends(create_smart_logger_dep("user"))
):
    # 业务逻辑
    user = await user_controller.create(user_data)
    return user
```

##### 2. 手动记录操作

```python
from utils.operation_logger import OperationLogger

# 在控制器或业务逻辑中手动记录
await OperationLogger.log_operation(
    user_id=current_user.id,
    user_name=current_user.username,
    module="user",
    table_name="users",
    record_id=user.id,
    action="CREATE",
    method="POST",
    path="/api/users",
    new_data={"username": "test", "nickname": "测试用户"},
    ip_address="192.168.1.1"
)
```

##### 3. 查询操作日志

```python
# 获取用户操作日志
logs = await OperationLog.filter(user_id=user_id).order_by("-created_at")

# 按模块查询
logs = await OperationLog.filter(module="user").order_by("-created_at")

# 按操作类型查询
logs = await OperationLog.filter(action="CREATE").order_by("-created_at")
```

#### 日志字段说明

| 字段 | 类型 | 描述 |
|------|------|------|
| user_id | int | 操作用户ID |
| user_name | str | 操作用户名 |
| module | str | 操作模块 |
| table_name | str | 操作表名 |
| record_id | int | 记录ID |
| action | str | 操作类型（CREATE/UPDATE/DELETE） |
| method | str | HTTP方法 |
| path | str | 请求路径 |
| old_data | json | 修改前数据 |
| new_data | json | 修改后数据 |
| ip_address | str | IP地址 |
| user_agent | str | 用户代理 |
| status | str | 操作状态（SUCCESS/FAILED） |
| error_message | text | 错误信息 |

### CRUD 增强功能

#### JSON 字段搜索

系统的 CRUD 基础类支持对 JSONB 字段进行深度搜索：

##### 使用方法

```python
# 假设 User 模型有一个 JSON 字段 user_extra
class User(AbstractBaseModel):
    username = fields.CharField(max_length=50)
    user_extra = fields.JSONField(null=True)  # 包含 {"name": "张三", "age": 25, "city": "北京"}

# 在搜索时，可以通过 user_extra.name 来搜索 JSON 字段内的 name 属性 并且完全匹配 仅支持一级
search_fields: list[str] = [
    "nickname"
]

users = await user_controller.list(params, UserResponse, search_fields)
```

### 添加新的权限

1. 在 `scripts/init_rbac.py` 中添加新权限：
```python
{"name": "新功能", "code": "feature:action", "resource": "feature", "action": "action", "description": "功能描述"}
```

2. 在需要的角色中分配权限

3. 在 API 中使用权限控制：
```python
@require_permissions("feature", "action")
async def new_feature():
    pass
```

### 扩展用户模型

如需扩展用户模型，编辑 `models/user.py`：

```python
class User(AbstractBaseModel):
    # 现有字段...
    phone = fields.CharField(max_length=20, null=True, description="手机号")
    email = fields.CharField(max_length=100, null=True, description="邮箱")
```

### 自定义权限验证

创建自定义权限验证装饰器：

```python
def require_custom_permission():
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 自定义权限逻辑
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```


## 📖 API 文档

启动应用后，可以通过以下地址查看详细的 API 文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- 在线文档: https://qlddchule5.apifox.cn/

## 🔒 安全考虑

1. **密码安全**: 使用 Argon2 算法加密存储密码
2. **JWT 安全**: 支持访问令牌和刷新令牌机制
3. **权限验证**: 多层次权限验证，防止权限绕过
4. **CORS 配置**: 可配置跨域访问控制
5. **环境变量**: 敏感信息通过环境变量配置

## 🤝 贡献指南

1. Fork 本项目
2. 创建特性分支: `git checkout -b feature/new-feature`
3. 提交更改: `git commit -am 'Add new feature'`
4. 推送分支: `git push origin feature/new-feature`
5. 提交 Pull Request

## 📄 许可证

本项目使用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 支持

如果您在使用过程中遇到问题，请通过以下方式获取帮助：

- 提交 [Issue](https://github.com/Anning01/fastapi-rbac-template/issues)
- 查看 [Wiki](https://github.com/Anning01/fastapi-rbac-template/wiki)
- 发送邮件至: anningforchina@gmail.com

## ✅ TODO

- [ ] 添加单元测试
- [ ] 添加 API 限流功能
- [ ] 支持多租户
- [x] 添加审计日志
- [ ] 支持权限继承
- [ ] 添加前端管理界面
- [x] 支持 OAuth 登录
- [ ] 添加数据备份恢复功能

---

⭐ 如果这个项目对您有帮助，请给个 Star 支持一下！