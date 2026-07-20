from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from config.database import Base


class Blog(Base):
    __tablename__ = "blogs"

    id = Column(Integer, primary_key=True, index=True)

    category_id = Column(
        Integer,
        ForeignKey("blog_categories.id"),
        nullable=False
    )

    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)

    short_description = Column(Text)
    description = Column(Text)

    featured_image = Column(String(255))

    seo_title = Column(String(255))
    meta_description = Column(Text)
    meta_keywords = Column(Text)
    tags = Column(Text)

    status = Column(Integer, default=1)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    category = relationship(
        "BlogCategory",
        back_populates="blogs"
    )