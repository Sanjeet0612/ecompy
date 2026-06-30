from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, SmallInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config.database import Base
from sqlalchemy.orm import relationship


class SubCategory(Base):
    __tablename__ = "sub_categories"

    id = Column(Integer, primary_key=True, index=True)

    category_id = Column(
        Integer,
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False
    )

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

    # Relationship
    category = relationship("Category", back_populates="subcategories")

    