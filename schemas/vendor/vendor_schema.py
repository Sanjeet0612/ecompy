from pydantic import BaseModel, EmailStr


class VendorSignup(BaseModel):
    name: str
    email: EmailStr
    password: str


class VendorLogin(BaseModel):
    email: EmailStr
    password: str
