from pydantic import BaseModel
from typing import Optional


class BrandCreate(BaseModel):
    name: str
    slug: str
    logo: Optional[str] = None


class BrandResponse(BaseModel):
    id: int
    name: str
    slug: str
    status: int

    class Config:
        from_attributes = True