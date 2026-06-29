from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
from config.database import Base


class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    profile_image = Column(String(255), nullable=True)

    role = Column(
        Enum("super_admin", "admin"),
        default="admin",
        nullable=False
    )

    status = Column(Integer, default=1, nullable=False)

    last_login = Column(DateTime, nullable=True)

    created_at = Column(
        DateTime,
        server_default=func.now()
    )

    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )