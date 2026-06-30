from sqlalchemy import Column, Integer, String, DateTime, SmallInteger
from sqlalchemy.sql import func
from config.database import Base
from sqlalchemy.orm import relationship


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(150), nullable=False)

    slug = Column(String(180), unique=True, nullable=False)

    image = Column(String(255), nullable=True)

    status = Column(SmallInteger, default=1)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    deleted_at = Column(DateTime(timezone=True), nullable=True)

    subcategories = relationship(
        "SubCategory",
        back_populates="category",
        cascade="all, delete-orphan"
    )