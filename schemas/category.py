from pydantic import BaseModel
from typing import Optional


class CategoryCreate(BaseModel):
    name: str
    slug: str
    image: Optional[str] = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    image: Optional[str] = None
    status: int

    class Config:
        from_attributes = True