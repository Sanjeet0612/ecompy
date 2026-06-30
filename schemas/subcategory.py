from pydantic import BaseModel
from typing import Optional


class SubCategoryCreate(BaseModel):
    category_id: int
    name: str
    slug: str
    image: Optional[str] = None


class SubCategoryResponse(BaseModel):
    id: int
    category_id: int
    name: str
    slug: str
    status: int

    class Config:
        from_attributes = True