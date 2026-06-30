from sqlalchemy import Column, Integer, ForeignKey, DateTime, SmallInteger, DECIMAL, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base


class ProductAttribute(Base):
    __tablename__ = "product_attributes"

    id = Column(Integer, primary_key=True, index=True)

    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    attribute_value_id = Column(Integer, ForeignKey("attribute_values.id", ondelete="CASCADE"), nullable=False)

    price = Column(DECIMAL(10,2), default=0)
    stock = Column(Integer, default=0)

    sku = Column(String(100), unique=True, nullable=True)

    status = Column(SmallInteger, default=1)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    product = relationship("Product", back_populates="variants")