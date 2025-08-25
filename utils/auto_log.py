#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @author:anning
# @email:anningforchina@gmail.com
# @time:2025/08/22 16:00
# @file:auto_log.py

from typing import Optional, Any
from fastapi import Request, Depends

from core.deps import get_current_active_user
from models.user import User
from utils.operation_logger import OperationLogger


class AutoLogger:
    """自动日志记录器"""

    def __init__(
        self,
        user: User,
        request: Request,
        module: str,
        table_name: Optional[str] = None,
    ):
        self.user = user
        self.request = request
        self.module = module
        self.table_name = table_name or module
        self.action = self._infer_action()

    def _infer_action(self) -> str:
        """根据HTTP方法推断操作类型"""
        method = self.request.method.upper()
        if method == "POST":
            return "CREATE"
        elif method in ["PUT", "PATCH"]:
            return "UPDATE"
        elif method == "DELETE":
            return "DELETE"
        return "READ"

    async def log_create(self, record_id: int, data: Any):
        """记录创建操作"""
        await OperationLogger.log_operation(
            user=self.user,
            request=self.request,
            action="CREATE",
            module=self.module,
            table_name=self.table_name,
            record_id=record_id,
            new_data=data,
            status="SUCCESS",
        )

    async def log_update(self, record_id: int, old_data: Any, new_data: Any):
        """记录更新操作"""
        await OperationLogger.log_operation(
            user=self.user,
            request=self.request,
            action="UPDATE",
            module=self.module,
            table_name=self.table_name,
            record_id=record_id,
            old_data=old_data,
            new_data=new_data,
            status="SUCCESS",
        )

    async def log_delete(self, record_id: int, data: Any):
        """记录删除操作"""
        await OperationLogger.log_operation(
            user=self.user,
            request=self.request,
            action="DELETE",
            module=self.module,
            table_name=self.table_name,
            record_id=record_id,
            old_data=data,
            status="SUCCESS",
        )

    async def log_error(
        self,
        error_message: str,
        record_id: Optional[int] = None,
        data: Optional[Any] = None,
    ):
        """记录错误操作"""
        await OperationLogger.log_operation(
            user=self.user,
            request=self.request,
            action=self.action,
            module=self.module,
            table_name=self.table_name,
            record_id=record_id,
            new_data=data,
            status="FAILED",
            error_message=error_message,
        )


def create_logger_with_permission(module: str, table_name: Optional[str] = None):
    """创建带权限检查的日志记录器依赖"""

    def get_logger(
        request: Request, current_user: User = Depends(get_current_active_user)
    ) -> AutoLogger:
        return AutoLogger(current_user, request, module, table_name or module)

    return get_logger


# 各模块的日志记录器
get_news_auto_logger = create_logger_with_permission("news")
get_user_auto_logger = create_logger_with_permission("user")
get_research_auto_logger = create_logger_with_permission("research")
get_survey_auto_logger = create_logger_with_permission("survey")
