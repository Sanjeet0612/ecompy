from pydantic import BaseModel
from typing import Optional


class BlogCreate(BaseModel):
    category_id: int
    title: str
    slug: str
    short_description: Optional[str] = None
    description: Optional[str] = None
    featured_image: Optional[str] = None
    seo_title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None
    tags: Optional[str] = None
    status: int = 1


class BlogUpdate(BaseModel):
    category_id: int
    title: str
    slug: str
    short_description: Optional[str] = None
    description: Optional[str] = None
    featured_image: Optional[str] = None
    seo_title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None
    tags: Optional[str] = None
    status: int


class BlogResponse(BaseModel):
    id: int
    category_id: int
    title: str
    slug: str
    short_description: Optional[str]
    description: Optional[str]
    featured_image: Optional[str]
    seo_title: Optional[str]
    meta_description: Optional[str]
    meta_keywords: Optional[str]
    tags: Optional[str]
    status: int

    class Config:
        from_attributes = True