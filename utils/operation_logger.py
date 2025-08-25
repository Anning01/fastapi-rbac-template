#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @author:anning
# @email:anningforchina@gmail.com
# @time:2025/08/22 15:00
# @file:operation_logger.py

import json
from typing import Any, Dict, Optional
from fastapi import Request
from models.operation_log import OperationLog
from models.user import User


class OperationLogger:
    """操作日志记录器"""

    @staticmethod
    async def log_operation(
        user: User,
        request: Request,
        action: str,
        module: str,
        table_name: Optional[str] = None,
        record_id: Optional[int] = None,
        old_data: Optional[Dict[str, Any]] = None,
        new_data: Optional[Dict[str, Any]] = None,
        status: str = "SUCCESS",
        error_message: Optional[str] = None,
    ) -> OperationLog:
        """
        记录操作日志

        Args:
            user: 操作用户
            request: 请求对象
            action: 操作类型 (CREATE, UPDATE, DELETE)
            module: 操作模块
            table_name: 操作表名
            record_id: 记录ID
            old_data: 修改前数据
            new_data: 修改后数据
            status: 操作状态 (SUCCESS, FAILED)
            error_message: 错误信息

        Returns:
            OperationLog: 创建的日志记录
        """

        # 获取客户端IP
        ip_address = OperationLogger._get_client_ip(request)

        # 获取用户代理
        user_agent = request.headers.get("user-agent")

        # 序列化数据
        old_data_json = None
        new_data_json = None

        if old_data:
            old_data_json = OperationLogger._serialize_data(old_data)

        if new_data:
            new_data_json = OperationLogger._serialize_data(new_data)

        # 创建日志记录
        operation_log = await OperationLog.create(
            user_id=user.id,
            user_name=user.nickname or user.username,
            module=module,
            table_name=table_name,
            record_id=record_id,
            action=action,
            method=request.method,
            path=str(request.url.path),
            old_data=old_data_json,
            new_data=new_data_json,
            ip_address=ip_address,
            user_agent=user_agent,
            status=status,
            error_message=error_message,
        )

        return operation_log

    @staticmethod
    def _get_client_ip(request: Request) -> Optional[str]:
        """获取客户端IP地址"""
        # 尝试从不同的头部获取真实IP
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # 获取客户端IP
        if request.client:
            return request.client.host

        return None

    @staticmethod
    def _serialize_data(data: Any) -> Optional[dict]:
        """序列化数据为JSON可存储格式"""
        try:
            # 如果是模型对象，转换为字典
            if hasattr(data, "__dict__"):
                # 过滤掉私有属性和方法
                return {
                    k: v
                    for k, v in data.__dict__.items()
                    if not k.startswith("_") and not callable(v)
                }
            elif isinstance(data, dict):
                return data
            else:
                # 尝试JSON序列化测试
                json.dumps(data)
                return data
        except (TypeError, ValueError):
            # 如果无法序列化，转换为字符串
            return {"serialized": str(data)}

        return None


async def log_create_operation(
    user: User,
    request: Request,
    module: str,
    table_name: str,
    record_id: int,
    data: Any,
    status: str = "SUCCESS",
    error_message: Optional[str] = None,
) -> OperationLog:
    """记录创建操作"""
    return await OperationLogger.log_operation(
        user=user,
        request=request,
        action="CREATE",
        module=module,
        table_name=table_name,
        record_id=record_id,
        new_data=data,
        status=status,
        error_message=error_message,
    )


async def log_update_operation(
    user: User,
    request: Request,
    module: str,
    table_name: str,
    record_id: int,
    old_data: Any,
    new_data: Any,
    status: str = "SUCCESS",
    error_message: Optional[str] = None,
) -> OperationLog:
    """记录更新操作"""
    return await OperationLogger.log_operation(
        user=user,
        request=request,
        action="UPDATE",
        module=module,
        table_name=table_name,
        record_id=record_id,
        old_data=old_data,
        new_data=new_data,
        status=status,
        error_message=error_message,
    )


async def log_delete_operation(
    user: User,
    request: Request,
    module: str,
    table_name: str,
    record_id: int,
    data: Any,
    status: str = "SUCCESS",
    error_message: Optional[str] = None,
) -> OperationLog:
    """记录删除操作"""
    return await OperationLogger.log_operation(
        user=user,
        request=request,
        action="DELETE",
        module=module,
        table_name=table_name,
        record_id=record_id,
        old_data=data,
        status=status,
        error_message=error_message,
    )
