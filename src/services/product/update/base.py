from typing import Type

from sqlalchemy.ext.asyncio import AsyncSession

from services.product.base import T


async def update_object(db: AsyncSession, model: Type[T], obj_id: int, **fileds) -> T | None:
    obj = await db.get(model, obj_id)
    if obj:
        for key, value in fileds.items():
            setattr(obj, key, value)
        
        await db.commit()
        await db.refresh(obj)

    return obj