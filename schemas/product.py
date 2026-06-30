from pydantic import BaseModel
from typing import Optional


class ProductCreate(BaseModel):
    vendor_id: int
    category_id: int
    subcategory_id: int
    brand_id: int

    name: str
    slug: str

    short_description: Optional[str] = None
    description: Optional[str] = None


class ProductResponse(BaseModel):
    id: int
    name: str
    slug: str
    status: int
    approval_status: int
    product_state: int

    class Config:
        from_attributes = True