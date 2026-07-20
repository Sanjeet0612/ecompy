from pydantic import BaseModel
from typing import Optional


class BlogCategoryCreate(BaseModel):
    name: str
    slug: str
    status: int = 1


class BlogCategoryUpdate(BaseModel):
    name: str
    slug: str
    status: int


class BlogCategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    status: int

    class Config:
        from_attributes = True