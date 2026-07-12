from sqlalchemy.orm import Session

from models.product_variant import ProductVariant


class ProductVariantRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        product_id: int,
        sku: str,
        price: float,
        stock: int,
        status: int = 1
    ):

        variant = ProductVariant(
            product_id=product_id,
            sku=sku,
            price=price,
            stock=stock,
            status=status
        )

        self.db.add(variant)
        self.db.flush()

        return variant