#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @author:anning
# @email:anningforchina@gmail.com
# @time:2025/08/22 16:00
# @file:smart_log.py
import importlib
from functools import wraps
from typing import Callable, Optional
from utils.auto_log import AutoLogger


def with_auto_log(module: str, table_name: Optional[str] = None):
    """
    智能自动日志装饰器

    使用方法：
    @with_auto_log("news")
    @router.post("/")
    async def create_news(..., auto_logger: AutoLogger = Depends(get_auto_logger)):
        # 业务逻辑
        pass
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 查找auto_logger参数
            auto_logger = None
            for key, value in kwargs.items():
                if isinstance(value, AutoLogger):
                    auto_logger = value
                    break

            if not auto_logger:
                # 如果没有auto_logger，直接执行
                return await func(*args, **kwargs)

            try:
                # 对于UPDATE和DELETE操作，先获取旧数据
                old_data = None
                record_id = None

                # 从kwargs中获取记录ID（FastAPI路径参数通常在kwargs中）
                for key, value in kwargs.items():
                    if key.endswith("_id") and isinstance(value, int):
                        record_id = value
                        break

                # 如果kwargs中没有，再从args中查找
                if not record_id:
                    for arg in args:
                        if isinstance(arg, int):
                            record_id = arg
                            break
                if record_id and auto_logger.action in ["UPDATE", "DELETE"]:
                    # 这里需要根据模块动态获取控制器
                    try:
                        # 动态导入对应的控制器
                        module_path = f"controllers.{module}"
                        controller_name = f"{module}_controller"
                        # 动态导入模块
                        controllers_module = importlib.import_module(module_path)
                        # 获取控制器实例
                        controller = getattr(controllers_module, controller_name)
                        if controller:
                            old_record = await controller.get(record_id)
                            if old_record:
                                old_data = old_record.__dict__.copy()
                                # 转换datetime对象为字符串
                                for key, value in old_data.items():
                                    if hasattr(
                                        value, "isoformat"
                                    ):  # datetime对象有isoformat方法
                                        old_data[key] = value.isoformat()
                    except Exception as e:
                        print(e)
                        pass  # 如果获取旧数据失败，继续执行

                # 执行原函数
                result = await func(*args, **kwargs)

                # 根据操作类型记录日志
                if auto_logger.action == "CREATE":
                    # 获取新创建的记录ID
                    if hasattr(result, "data") and (hasattr(result.data, "id") or (isinstance(result.data, (list, tuple)) and any(hasattr(item, "id") for item in result.data))):
                        if isinstance(result.data, dict):
                            record_id = result.data.id
                        # 从kwargs中查找创建数据（Pydantic model）
                        for key, value in kwargs.items():
                            if hasattr(value, "model_dump"):
                                create_data = value.model_dump()
                                await auto_logger.log_create(record_id, create_data)
                                break
                    else:
                        # 如果是自定义的一些接口，需要记录返回的message
                        if hasattr(result, "message"):
                            await auto_logger.log_create(record_id, {"message": result.message})

                elif auto_logger.action == "UPDATE" and record_id:
                    # 从kwargs中查找更新数据（Pydantic model）
                    for key, value in kwargs.items():
                        if hasattr(value, "model_dump"):
                            new_data = value.model_dump(exclude_unset=True)
                            await auto_logger.log_update(record_id, old_data, new_data)
                            break
                        else:
                            # 如果是自定义的一些接口，需要记录返回的message
                            if hasattr(result, "message"):
                                await auto_logger.log_update(record_id, old_data, {"message": result.message})
                elif auto_logger.action == "DELETE" and record_id and old_data:
                    await auto_logger.log_delete(record_id, old_data)

                return result

            except Exception as e:
                # 记录错误
                error_data = None
                for key, value in kwargs.items():
                    if hasattr(value, "model_dump"):
                        error_data = value.model_dump()
                        break
                await auto_logger.log_error(str(e), record_id, error_data)
                raise

        return wrapper

    return decorator


# 创建各模块的智能日志依赖
def create_smart_logger_dep(module: str, table_name: Optional[str] = None):
    """创建智能日志记录器依赖"""
    from utils.auto_log import create_logger_with_permission

    return create_logger_with_permission(module, table_name)
