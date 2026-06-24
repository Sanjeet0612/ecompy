from pydantic import BaseModel, EmailStr, Field, field_validator

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str | None = None
    password: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("Name is required.")

        if len(value) < 2:
            raise ValueError("Name must be at least 2 characters long.")

        if len(value) > 50:
            raise ValueError("Name must not exceed 50 characters.")

        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if not value:
            raise ValueError("Password is required.")

        if len(value) < 6:
            raise ValueError("Password must be at least 6 characters long.")

        if len(value) > 50:
            raise ValueError("Password must not exceed 50 characters.")

        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value):
        if value is None or value == "":
            return value

        if not value.isdigit():
            raise ValueError("Phone number must contain only digits.")

        if len(value) != 10:
            raise ValueError("Phone number must be exactly 10 digits.")

        return value