from pydantic import BaseModel


class AttributeCreate(BaseModel):
    name: str


class AttributeResponse(BaseModel):
    id: int
    name: str
    status: int

    class Config:
        from_attributes = True