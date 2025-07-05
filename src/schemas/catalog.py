from pydantic import BaseModel, Field

class CatalogBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255, example="Электроника")

class CatalogCreate(CatalogBase):
    pass

class CatalogUpdate(BaseModel):
    old_name: str = Field(..., description="Текущее название каталога")
    new_name: str = Field(..., min_length=2, max_length=255, description="Новое название")

class CatalogDelete(CatalogBase):
    pass

class CatalogResponse(CatalogBase):
    id: int
    is_available: bool

    class Config:
        from_attributes = True

'''
Можно будет добавить total_page, чтобы просматривать по страничкам, 
чтобы не было очень длинного списка за раз
'''
class CatalogListResponse(BaseModel):
    items: list[CatalogResponse]
    count: int