from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Type
from pydantic import BaseModel

from database.models import Catalog
from schemas.catalog import CatalogCreate, CatalogUpdate, CatalogResponse, CatalogListResponse

class CatalogService:
    @staticmethod
    def _validate_with_schema(
        item: Catalog,
        schema_type: Type[BaseModel]
    ) -> BaseModel:
        
        if not item:
            raise ValueError("Каталог не найден")
        
        return schema_type.model_validate(item)
    
    # Проверяет, что каталога с таким именем нет
    @staticmethod
    async def _ensure_catalog_not_exists(name: str, db: AsyncSession) -> None:

        existing = await CatalogService.get_catalog_by_name(name, db, None)
        if existing:
            raise ValueError(f"Каталог '{name}' уже существует")
    
    @staticmethod
    async def get_catalog_by_name(
        name: str,
        db: AsyncSession,
        schema_type: Type[BaseModel] = CatalogResponse
    ) -> BaseModel:
        
        result = await db.execute( 
            select(Catalog).where(Catalog.name == name)
        )
        catalog = result.scalar_one_or_none()

        return CatalogService._validate_with_schema(catalog, schema_type)
    
    @staticmethod
    async def create_catalog(
        data: CatalogCreate,
        db: AsyncSession
    ) -> CatalogResponse:
        
        await CatalogService._ensure_catalog_not_exists(data.name, db)
        
        catalog = Catalog(name=data.name)
        db.add(catalog)

        try:
            await db.commit()
            await db.refresh(catalog)

        except Exception as e:
            await db.rollback()
            raise RuntimeError("Ошибка при создании каталога") from e

        return CatalogService._validate_with_schema(catalog, CatalogResponse)
    
    @staticmethod
    async def update_catalog(
        data: CatalogUpdate,
        db: AsyncSession
    ) -> CatalogResponse:
        
        old_catalog = await CatalogService.get_catalog_by_name(data.old_name, db, None)
        if not old_catalog:
            raise ValueError("Каталог для обновления не найден")
        
        if data.old_name != data.new_name:  # Оптимизация: не проверяем, если имя не изменилось
            await CatalogService._ensure_catalog_not_exists(data.new_name, db)
            old_catalog.name = data.new_name
        
        try:
            await db.commit()
            await db.refresh(old_catalog)

        except Exception as e:
            await db.rollback()
            raise RuntimeError("Ошибка при обновлении каталога") from e
        
        return CatalogService._validate_with_schema(old_catalog, CatalogResponse)

    @staticmethod
    async def delete_catalog(
        name: str,
        db: AsyncSession
    ) -> bool:
        
        result = await db.execute(
            delete(Catalog).where(Catalog.name == name).returning(Catalog)
        )
        
        if not result.scalar_one_or_none():
            raise ValueError("Каталог не найден")
        await db.commit()

        return True

    @staticmethod
    async def get_all_catalogs(db: AsyncSession) -> CatalogListResponse:

        result = await db.execute(select(Catalog))
        catalogs = result.scalars().all()
        
        return CatalogListResponse(
            items=[CatalogResponse.model_validate(c) for c in catalogs],
            count=len(catalogs)
        )
