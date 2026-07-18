from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship

from config.database import Base


class BlogCategory(Base):
    __tablename__ = "blog_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    status = Column(Integer, default=1)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    blogs = relationship("Blog", back_populates="category")