from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, SmallInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base


class AttributeValue(Base):
    __tablename__ = "attribute_values"

    id = Column(Integer, primary_key=True, index=True)

    attribute_id = Column(
        Integer,
        ForeignKey("attributes.id", ondelete="CASCADE"),
        nullable=False
    )

    value = Column(String(100), nullable=False)

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

    # Relationship
    attribute = relationship("Attribute", back_populates="attribute_values")

    product_variant_values = relationship(
        "ProductVariantValue",
        back_populates="attribute_value",
        cascade="all, delete-orphan"
)