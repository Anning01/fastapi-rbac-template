#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @author:anning
# @email:anningforchina@gmail.com
# @time:2025/08/22 15:00
# @file:operation_log.py

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class OperationLogBase(BaseModel):
    user_id: int
    user_name: str
    module: str
    table_name: Optional[str] = None
    record_id: Optional[int] = None
    action: str  # CREATE, UPDATE, DELETE
    method: str
    path: str
    old_data: Optional[dict] = None
    new_data: Optional[dict] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    status: str  # SUCCESS, FAILED
    error_message: Optional[str] = None


class OperationLogCreate(OperationLogBase):
    pass


class OperationLogResponse(OperationLogBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
