from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, SmallInteger, Enum, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base



class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    vendor_id = Column(Integer, nullable=False, default=0)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    subcategory_id = Column(Integer, ForeignKey("sub_categories.id", ondelete="CASCADE"), nullable=False)
    brand_id = Column(Integer, ForeignKey("brands.id", ondelete="CASCADE"), nullable=False)

    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)

    short_description = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    main_image = Column(String(255), nullable=True)
    has_variant = Column(SmallInteger, default=0)

    sku = Column(String(100), unique=True, nullable=True)
    price = Column(DECIMAL(10, 2), default=0.00)
    stock = Column(Integer, default=0)

    status = Column(SmallInteger, default=1)
    approval_status = Column(SmallInteger, default=0)

    product_state = Column(SmallInteger, default=0)

    is_featured = Column(SmallInteger, default=0)

    sort_order = Column(Integer, default=0)

    commission_type = Column(
        Enum("fixed", "percentage"),
        nullable=True
    )

    commission_value = Column(
        DECIMAL(10,2),
        nullable=True
    )

    approved_by = Column(Integer,ForeignKey("users.id"),nullable=True)
    approved_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    variants = relationship("ProductVariant",back_populates="product",cascade="all, delete-orphan")