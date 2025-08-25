#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @author:anning
# @email:anningforchina@gmail.com
# @time:2025/08/22 15:00
# @file:operation_log.py

from fastapi import APIRouter, Depends, HTTPException

from controllers.operation_log import operation_log_crud
from models.operation_log import OperationLog
from models.user import User
from schemas.operation_log import OperationLogResponse
from schemas.page import QueryParams, get_list_params
from utils.common import ResponseSchema, PaginationResponse
from utils.rbac import get_current_superuser_or_permission

router = APIRouter()


@router.get(
    "/",
    summary="获取操作日志列表",
    response_model=ResponseSchema[PaginationResponse[OperationLogResponse]],
)
async def get_operation_logs(
    params: QueryParams = Depends(get_list_params),
    current_user: User = Depends(
        get_current_superuser_or_permission("operation_log", "read")
    ),
):
    """获取操作日志列表（分页）"""
    search_fields: list[str] = ["user_name", "module", "action", "path"]
    operation_logs = await operation_log_crud.list(
        params, OperationLogResponse, search_fields
    )
    return ResponseSchema(data=operation_logs)


@router.get(
    "/{log_id}",
    summary="获取操作日志详情",
    response_model=ResponseSchema[OperationLogResponse],
)
async def get_operation_log(
    log_id: int,
    current_user: User = Depends(
        get_current_superuser_or_permission("operation_log", "read")
    ),
):
    """获取操作日志详情"""
    operation_log = await operation_log_crud.get(log_id)
    if not operation_log:
        raise HTTPException(status_code=404, detail="操作日志不存在")
    return ResponseSchema(data=operation_log)


@router.get(
    "/user/{user_id}",
    summary="获取指定用户的操作日志",
    response_model=ResponseSchema[PaginationResponse[OperationLogResponse]],
)
async def get_user_operation_logs(
    user_id: int,
    params: QueryParams = Depends(get_list_params),
    current_user: User = Depends(
        get_current_superuser_or_permission("operation_log", "read")
    ),
):
    """获取指定用户的操作日志"""
    queryset = OperationLog.filter(user_id=user_id)
    operation_logs = await operation_log_crud.list_with_queryset(
        queryset, params, OperationLogResponse
    )
    return ResponseSchema(data=operation_logs)


@router.get(
    "/module/{module_name}",
    summary="获取指定模块的操作日志",
    response_model=ResponseSchema[PaginationResponse[OperationLogResponse]],
)
async def get_module_operation_logs(
    module_name: str,
    params: QueryParams = Depends(get_list_params),
    current_user: User = Depends(
        get_current_superuser_or_permission("operation_log", "read")
    ),
):
    """获取指定模块的操作日志"""
    queryset = OperationLog.filter(module=module_name)
    operation_logs = await operation_log_crud.list_with_queryset(
        queryset, params, OperationLogResponse
    )
    return ResponseSchema(data=operation_logs)
