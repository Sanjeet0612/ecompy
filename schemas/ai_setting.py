from pydantic import BaseModel
from typing import Optional


class AISettingUpdate(BaseModel):

    provider: str

    model: str

    temperature: float

    top_p: float

    max_output_tokens: int

    language: str

    description_length: str

    generate_seo: int

    generate_tags: int

    generate_specifications: int

    system_prompt: Optional[str] = None

    status: int


class AISettingResponse(BaseModel):

    id: int

    provider: str

    model: str

    temperature: float

    top_p: float

    max_output_tokens: int

    language: str

    description_length: str

    generate_seo: int

    generate_tags: int

    generate_specifications: int

    system_prompt: Optional[str]

    status: int

    class Config:
        from_attributes = True
