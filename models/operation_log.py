#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @author:anning
# @email:anningforchina@gmail.com
# @time:2025/08/22 15:00
# @file:operation_log.py

from tortoise import fields

from models._base import AbstractBaseModel


class OperationLog(AbstractBaseModel):
    """操作日志模型"""

    user_id = fields.IntField(description="操作用户ID")
    user_name = fields.CharField(max_length=100, description="操作用户名")
    module = fields.CharField(max_length=50, description="操作模块")
    table_name = fields.CharField(max_length=50, description="操作表名", null=True)
    record_id = fields.IntField(description="记录ID", null=True)
    action = fields.CharField(
        max_length=20, description="操作类型"
    )  # CREATE, UPDATE, DELETE
    method = fields.CharField(max_length=10, description="HTTP方法")
    path = fields.CharField(max_length=200, description="请求路径")
    old_data = fields.JSONField(description="修改前数据", null=True)
    new_data = fields.JSONField(description="修改后数据", null=True)
    ip_address = fields.CharField(max_length=45, description="IP地址", null=True)
    user_agent = fields.TextField(description="用户代理", null=True)
    status = fields.CharField(max_length=10, description="操作状态")  # SUCCESS, FAILED
    error_message = fields.TextField(description="错误信息", null=True)

    class Meta:
        table = "operation_logs"
        table_description = "操作日志表"
