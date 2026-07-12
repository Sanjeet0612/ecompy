from sqlalchemy.orm import Session

from models.product_variant_value import ProductVariantValue


class ProductVariantValueRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        variant_id: int,
        attribute_value_id: int
    ):

        variant_value = ProductVariantValue(
            variant_id=variant_id,
            attribute_value_id=attribute_value_id
        )

        self.db.add(variant_value)

        return variant_value