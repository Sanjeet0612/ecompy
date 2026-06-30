from sqlalchemy import Column, Integer, String, DateTime, SmallInteger
from sqlalchemy.sql import func
from config.database import Base
from sqlalchemy.orm import relationship


class Attribute(Base):
    __tablename__ = "attributes"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False, unique=True)

    status = Column(SmallInteger, default=1)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    deleted_at = Column(DateTime(timezone=True), nullable=True)

    attribute_values = relationship(
        "AttributeValue",
        back_populates="attribute",
        cascade="all, delete-orphan"
    )