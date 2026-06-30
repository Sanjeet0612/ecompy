from pydantic import BaseModel
from typing import Optional


class ProductAttributeCreate(BaseModel):
    product_id: int
    attribute_value_id: int

    price: float
    stock: int

    sku: Optional[str] = None


class ProductAttributeResponse(BaseModel):
    id: int
    product_id: int
    attribute_value_id: int
    price: float
    stock: int
    sku: Optional[str]

    class Config:
        from_attributes = True