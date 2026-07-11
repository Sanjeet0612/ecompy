from pydantic import BaseModel
from typing import Optional,Literal


class CategoryCreate(BaseModel):
    name: str
    slug: str
    image: Optional[str] = None
    commission_type: Literal["fixed", "percentage"] = "percentage"
    commission_value: float = 0.00


class CategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    image: Optional[str] = None
    commission_type: str
    commission_value: float
    status: int

    class Config:
        from_attributes = True