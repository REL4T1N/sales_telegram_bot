from typing import Type, TypeVar
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import select

T = TypeVar("T", bound=DeclarativeBase)


async def get_all(db: AsyncSession, model: Type[T]) -> list[T]:
    result = await db.execute(select(model))
    return result.scalars().all()


async def create_object(db: AsyncSession, model: Type[T], **kwargs) -> T:
    obj = model(**kwargs)
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj
