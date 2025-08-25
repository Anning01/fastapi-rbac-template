from core.crud import CRUDBase
from models.operation_log import OperationLog
from schemas.page import QueryParams


class OperationLogCRUD(CRUDBase[OperationLog, None, None]):
    async def list_with_queryset(
        self,
        base_query,
        params: QueryParams,
        response_model,
    ):
        """使用指定的查询集进行分页查询"""
        return await self.list(params, response_model, base_query=base_query)


operation_log_crud = OperationLogCRUD(OperationLog)