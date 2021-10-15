from typing import Any
from typing import List
from typing import Optional

from fastapi import HTTPException

from pydantic_aioredis import Model


class FastAPIModel(Model):
    """
    Useful with fastapi, offers extra class methods specific to using pydantic_aioredis with Fastapi
    """

    @classmethod
    async def select_or_404(
        cls,
        columns: Optional[List[str]] = None,
        ids: Optional[List[Any]] = None,
        custom_exception: Optional[Exception] = None,
    ):
        """
        Selects given rows or sets of rows in the table.
        Raises a HTTPException with a 404 if there is no result
        """
        result = await cls.select(columns=columns, ids=ids)
        if result is None:
            raise HTTPException(
                status_code=404, detail=f"{cls.__name__} not found"
            ) if custom_exception is None else custom_exception
        return result
