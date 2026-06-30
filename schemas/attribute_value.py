from pydantic import BaseModel


class AttributeValueCreate(BaseModel):
    attribute_id: int
    value: str


class AttributeValueResponse(BaseModel):
    id: int
    attribute_id: int
    value: str
    status: int

    class Config:
        from_attributes = True