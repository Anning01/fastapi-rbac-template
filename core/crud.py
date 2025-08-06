from typing import (
    Any,
    Dict,
    Generic,
    NewType,
    Type,
    TypeVar,
    Union,
    Optional,
)

from pydantic import BaseModel
from tortoise.models import Model
from tortoise.queryset import QuerySet

from schemas.page import QueryParams, QueryBuilder

T = TypeVar("T")
Total = NewType("Total", int)
ModelType = TypeVar("ModelType", bound=Model)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, id: int, base_query: Optional[QuerySet] = None) -> ModelType:
        if base_query:
            base_query = base_query.filter(id=id)
            return await base_query.first()
        return await self.model.get(id=id)

    async def list(
        self,
        params: QueryParams,
        response_model: Type[BaseModel],
        search_fields: Optional[list[str]] = None,
        base_query: Optional[QuerySet] = None,
    ) -> dict[str, dict[str, int | Any] | Any]:
        if base_query is None:
            query = self.model.all()
        else:
            query = base_query
        #  应用过滤
        query = await QueryBuilder.apply_filters(
            query, self.model, params.filters or {}
        )

        # 应用搜索
        query = await QueryBuilder.apply_search(
            query, params.search, search_fields or []
        )

        # 计算总数
        total = await query.count()

        # 应用排序
        query = await QueryBuilder.apply_sorting(query, params.sort)

        # 应用分页
        paginated_query = await QueryBuilder.apply_pagination(
            query, params.page, params.page_size
        )

        # 执行查询
        items = await paginated_query

        # 计算分页信息
        pages = (total + params.page_size - 1) // params.page_size if total > 0 else 0

        items_pydantic = [response_model.model_validate(item) for item in items]

        results = {
            "items": items_pydantic,
            "pagination": {
                "total": total,
                "page": params.page,
                "page_size": params.page_size,
                "pages": pages,
            },
        }

        return results

    async def create(self, obj_in: CreateSchemaType, **kwargs) -> ModelType:
        if isinstance(obj_in, Dict):
            obj_dict = obj_in
        else:
            obj_dict = obj_in.model_dump()
        obj = self.model(**obj_dict, **kwargs)
        await obj.save()
        return obj

    async def update(
        self, instance: ModelType, obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        if isinstance(obj_in, Dict):
            obj_dict = obj_in
        else:
            obj_dict = obj_in.model_dump(exclude_unset=True, exclude={"id"})
        obj = instance.update_from_dict(obj_dict)
        await obj.save()
        return obj

    async def remove(self, obj: ModelType) -> None:
        await obj.delete()
