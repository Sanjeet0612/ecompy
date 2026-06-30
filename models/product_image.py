from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, SmallInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base


class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(Integer, primary_key=True, index=True)

    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)

    image = Column(String(255), nullable=False)

    is_thumbnail = Column(SmallInteger, default=0)

    sort_order = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    product = relationship("Product", back_populates="images")