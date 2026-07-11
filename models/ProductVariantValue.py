from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from config.database import Base


class ProductVariantValue(Base):
    __tablename__ = "product_variant_values"

    id = Column(Integer, primary_key=True, index=True)

    variant_id = Column(
        Integer,
        ForeignKey("product_variants.id", ondelete="CASCADE"),
        nullable=False
    )

    attribute_value_id = Column(
        Integer,
        ForeignKey("attribute_values.id", ondelete="CASCADE"),
        nullable=False
    )

    # Relationships
    variant = relationship(
        "ProductVariant",
        back_populates="variant_values"
    )

    attribute_value = relationship(
        "AttributeValue"
    )