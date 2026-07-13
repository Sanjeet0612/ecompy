from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, SmallInteger, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base


class ProductVariant(Base):
    __tablename__ = "product_variants"

    id = Column(Integer, primary_key=True, index=True)

    product_id = Column(
        Integer,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False
    )

    sku = Column(String(100), unique=True, nullable=True)

    price = Column(DECIMAL(10, 2), default=0.00, nullable=False)

    stock = Column(Integer, default=0, nullable=False)

    status = Column(SmallInteger, default=1, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    product = relationship("Product", back_populates="variants")

    variant_values = relationship(
        "ProductVariantValue",
        back_populates="variant",
        cascade="all, delete-orphan"
    )