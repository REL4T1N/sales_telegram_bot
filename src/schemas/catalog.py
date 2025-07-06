from pydantic import BaseModel

class ProductCreate(BaseModel):
    category_id: int
    unit_id: int
    available: bool = True
    size: float
    quantity: float
    price: float