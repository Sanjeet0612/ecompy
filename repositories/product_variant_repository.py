from sqlalchemy.orm import Session
from models.product_variant import ProductVariant
from repositories.product_variant_value_repository import ProductVariantValueRepository


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
    
    # Delete Variant By Product
    def delete_by_product(
        self,
        product_id: int
    ):
        self.db.query(ProductVariant).filter(
            ProductVariant.product_id == product_id
        ).delete(synchronize_session=False)



    # Save Product Variants
    def save_variants(
        self,
        product_id: int,
        variant_value_ids: list[str],
        variant_sku: list[str],
        variant_price: list[float],
        variant_stock: list[int],
        variant_status: list[int]
    ):

        variant_value_repository = ProductVariantValueRepository(self.db)

        for index in range(len(variant_value_ids)):

            variant = self.create(
                product_id=product_id,
                sku=variant_sku[index],
                price=variant_price[index],
                stock=variant_stock[index],
                status=variant_status[index]
            )

            attribute_values = variant_value_ids[index].split(",")

            for attribute_value_id in attribute_values:

                attribute_value_id = attribute_value_id.strip()

                if not attribute_value_id:
                    continue

                variant_value_repository.create(
                    variant_id=variant.id,
                    attribute_value_id=int(attribute_value_id)
                )    