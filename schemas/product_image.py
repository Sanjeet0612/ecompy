from pydantic import BaseModel


class ProductImageCreate(BaseModel):
    product_id: int
    image: str
    is_thumbnail: int = 0
    sort_order: int = 0


class ProductImageResponse(BaseModel):
    id: int
    product_id: int
    image: str
    is_thumbnail: int

    class Config:
        from_attributes = True