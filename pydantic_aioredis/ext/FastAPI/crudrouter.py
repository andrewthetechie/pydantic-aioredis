from typing import Any
from typing import Callable
from typing import cast
from typing import List
from typing import Optional
from typing import Type
from typing import Union

from fastapi_crudrouter.core import CRUDGenerator
from fastapi_crudrouter.core import NOT_FOUND
from fastapi_crudrouter.core._types import DEPENDENCIES
from fastapi_crudrouter.core._types import PAGINATION
from fastapi_crudrouter.core._types import PYDANTIC_SCHEMA as SCHEMA

from pydantic_aioredis.store import Store


CALLABLE = Callable[..., SCHEMA]
CALLABLE_LIST = Callable[..., List[SCHEMA]]


class PydanticAioredisCRUDRouter(CRUDGenerator[SCHEMA]):
    def __init__(
        self,
        schema: Type[SCHEMA],
        store: Store,
        create_schema: Optional[Type[SCHEMA]] = None,
        update_schema: Optional[Type[SCHEMA]] = None,
        prefix: Optional[str] = None,
        tags: Optional[List[str]] = None,
        paginate: Optional[int] = None,
        get_all_route: Union[bool, DEPENDENCIES] = True,
        get_one_route: Union[bool, DEPENDENCIES] = True,
        create_route: Union[bool, DEPENDENCIES] = True,
        update_route: Union[bool, DEPENDENCIES] = True,
        delete_one_route: Union[bool, DEPENDENCIES] = True,
        delete_all_route: Union[bool, DEPENDENCIES] = True,
        **kwargs: Any
    ) -> None:
        super().__init__(
            schema=schema,
            create_schema=create_schema,
            update_schema=update_schema,
            prefix=prefix,
            tags=tags,
            paginate=paginate,
            get_all_route=get_all_route,
            get_one_route=get_one_route,
            create_route=create_route,
            update_route=update_route,
            delete_one_route=delete_one_route,
            delete_all_route=delete_all_route,
            **kwargs
        )
        self.store = store
        self.store.register_model(self.schema)

    def _get_all(self, *args: Any, **kwargs: Any) -> CALLABLE_LIST:
        async def route(
            pagination: PAGINATION = self.pagination,
        ) -> List[SCHEMA]:
            skip, limit = pagination.get("skip"), pagination.get("limit")
            skip = cast(int, skip)
            models = await self.schema.select(skip=skip, limit=limit)
            return models if models is not None else []

        return route

    def _get_one(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(item_id: str) -> SCHEMA:
            model = await self.schema.select(ids=[item_id])
            if model is None:
                raise NOT_FOUND
            return model[0]

        return route

    def _create(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(model: self.create_schema) -> SCHEMA:  # type: ignore
            model = self.schema(**model.dict())
            await self.schema.insert(model)
            return model

        return route

    def _update(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(item_id: str, model: self.update_schema) -> SCHEMA:  # type: ignore
            if await self.schema.select(ids=[item_id]) is None:
                raise NOT_FOUND
            await self.schema.update(item_id, data=model.dict())
            result = await self.schema.select(ids=item_id)
            return result[0]

        return route

    def _delete_all(self, *args: Any, **kwargs: Any) -> CALLABLE_LIST:
        async def route() -> List[SCHEMA]:
            await self.schema.delete()
            return []

        return route

    def _delete_one(self, *args: Any, **kwargs: Any) -> CALLABLE:
        async def route(item_id: str) -> SCHEMA:
            model = await self.schema.select(ids=[item_id])
            if model is None:
                raise NOT_FOUND
            await self.schema.delete(ids=[item_id])
            return model[0]

        return route
