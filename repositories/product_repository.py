from sqlalchemy.orm import Session

from models.product import Product
from schemas.product import ProductCreate


class ProductRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, product_data: ProductCreate):

        product = Product(
            vendor_id=product_data.vendor_id,
            category_id=product_data.category_id,
            subcategory_id=product_data.subcategory_id,
            brand_id=product_data.brand_id,

            name=product_data.name,
            slug=product_data.slug,

            sku=product_data.sku,
            price=product_data.price,
            stock=product_data.stock,

            commission_type=product_data.commission_type,
            commission_value=product_data.commission_value,

            short_description=product_data.short_description,
            description=product_data.description,

            main_image=product_data.main_image,

            has_variant=product_data.has_variant,
            status=product_data.status,
        )

        self.db.add(product)
        self.db.flush()

        return product