from typing import Type

from sqlalchemy.ext.asyncio import AsyncSession

from services.product.base import T


async def create_object(db: AsyncSession, model: Type[T], **kwargs) -> T:
    obj = model(**kwargs)
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj