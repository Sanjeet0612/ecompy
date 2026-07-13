from sqlalchemy.orm import Session
from models.product import Product
from schemas.product import ProductCreate
from models.product_image import ProductImage
from models.product_variant import ProductVariant
from models.product_variant_value import ProductVariantValue


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
    
# Gallery Section 
    def save_gallery_images(self, product_id: int, images: list[str]):

        sort_order = 1

        for image in images:
            product_images = ProductImage(
                product_id=product_id,
                image=image,
                sort_order=sort_order
            )

            self.db.add(product_images)

            sort_order += 1

        self.db.flush()

# Variant Section 

    def save_variants(self,product_id: int,variants: list):

        variant_ids = []

        for variant in variants:
            product_variant = ProductVariant(
                product_id=product_id,
                sku=variant["sku"],
                price=variant["price"],
                stock=variant["stock"],
                status=variant["status"]
            )

            self.db.add(product_variant)
            self.db.flush()

            variant_ids.append({
                "variant_id": product_variant.id,
                "attribute_value_ids": variant["attribute_value_ids"]
            })

        return variant_ids 
    
# Variant Value Section

    def save_variant_values(self, variant_data: list):

        for item in variant_data:

            variant_id = item["variant_id"]

            for attribute_value_id in item["attribute_value_ids"]:

                product_variant_value = ProductVariantValue(
                    variant_id=variant_id,
                    attribute_value_id=attribute_value_id
                )

                self.db.add(product_variant_value)

        self.db.flush()    
    