from sqlalchemy.orm import Session
from models.product import Product
from schemas.product import ProductCreate, ProductUpdate
from models.product_image import ProductImage
from models.product_variant import ProductVariant
from models.product_variant_value import ProductVariantValue
from models.attribute_value import AttributeValue
from sqlalchemy.orm import joinedload
from math import ceil
from sqlalchemy import or_
from datetime import datetime


class ProductRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self,
        db,
        page: int = 1,
        limit: int = 10,
        search: str = "",
        status: str = "",
        category_id: int | None = None,
        subcategory_id: int | None = None,
    ):

        query = ( 
                db.query(Product)
                .filter(Product.deleted_at.is_(None))
                .options(
                    joinedload(Product.category),
                    joinedload(Product.subcategory),
                    joinedload(Product.brand)
                )
            )
        
        
        # Search
        if search:

            query = query.filter(
                or_(
                    Product.name.ilike(f"%{search}%"),
                    Product.sku.ilike(f"%{search}%"),
                    Product.slug.ilike(f"%{search}%")
                )
            )

        # Status
        if status != "":
            query = query.filter(Product.status == int(status))

        if category_id:
            query = query.filter(Product.category_id == category_id)

        if subcategory_id:
            query = query.filter(Product.subcategory_id == subcategory_id)    

        total = query.count()

        products = (
            query.order_by(Product.id.desc())
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )

        data = []

        for product in products:

            data.append({

                "id": product.id,

                "name": product.name,

                "slug": product.slug,

                "sku": product.sku,

                "category": (
                    product.category.name
                    if product.category
                    else "-"
                ),

                "brand": (
                    product.brand.name
                    if product.brand
                    else "-"
                ),

                "price": product.price,

                "stock": product.stock,

                "orders": 0,

                "status": product.status,

                "approval_status": product.approval_status,

                "is_featured": product.is_featured,

                "main_image": product.main_image,

                "updated_at_date": (
                    product.updated_at.strftime("%d %b, %Y")
                    if product.updated_at
                    else "-"
                ),

                "updated_at_time": (
                    product.updated_at.strftime("%I:%M %p")
                    if product.updated_at
                    else "-"
                )

            })

        return {

            "data": data,

            "total": total,

            "page": page,

            "limit": limit,

            "total_pages": ceil(total / limit) if limit else 1

        }

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
            seo_title = product_data.seo_title,
            meta_description = product_data.meta_description,
            meta_keywords = product_data.meta_keywords,
            tags = product_data.tags,
            main_image=product_data.main_image,
            has_variant=product_data.has_variant,
            status=product_data.status,
            is_featured=product_data.is_featured,
            
        )

        self.db.add(product)
        self.db.flush()

        return product
    
    # Gallery Section 
    def save_gallery_images(self, product_id: int, images: list[str]):
       
        sort_order = 1

        for image in images:
            print("Adding:", image)

            product_images = ProductImage(
                product_id=product_id,
                image=image,
                sort_order=sort_order
            )

            self.db.add(product_images)

            sort_order += 1

        self.db.flush()
        self.db.commit()
        
    
    # Gallery Image By Product Id
    def get_gallery_images(self, product_id: int):
        return (
            self.db.query(ProductImage)
            .filter(ProductImage.product_id == product_id)
            .order_by(ProductImage.sort_order)
            .all()
        )

    # Delete Gallery Image

    def delete_gallery_image(self, image_id: int):
        image = (
            self.db.query(ProductImage)
            .filter(ProductImage.id == image_id)
            .first()
        )

        if image:
            self.db.delete(image)
            self.db.flush()

        return image
    
    # Delete All Gallery

    def delete_all_gallery_images(self, product_id: int):
        self.db.query(ProductImage).filter(
            ProductImage.product_id == product_id
        ).delete()

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
    
    # Delete By Id  Section
    
    def delete(
        self, db, product_id
    ):

        try:
            product = (
                db.query(Product)
                .filter(
                    Product.id == product_id,
                    Product.deleted_at.is_(None)
                )
                .first()
            )

            if not product:

                return {
                    "status": False,
                    "message": "Product not found."
                }

            product.deleted_at = datetime.utcnow()

            db.commit()

            return {
                "status": True,
                "message": "Product deleted successfully."
            }

        except Exception as e:

            db.rollback()

            return {
                "status": False,
                "message": str(e)
            }

    # Bulk Delete Section

    def bulk_delete(
        self,
        product_ids: list[int]
    ):

        try:

            if not product_ids:

                return {
                    "status": False,
                    "message": "No products selected."
                }

            deleted_count = (
                self.db.query(Product)
                .filter(
                    Product.id.in_(product_ids),
                    Product.deleted_at.is_(None)
                )
                .update(
                    {
                        Product.deleted_at: datetime.utcnow(),
                        Product.updated_at: datetime.utcnow()
                    },
                    synchronize_session=False
                )
            )

            self.db.commit()

            return {
                "status": True,
                "message": f"{deleted_count} product(s) deleted successfully."
            }

        except Exception as e:

            self.db.rollback()

            return {
                "status": False,
                "message": str(e)
            }   

    # Get Product By Id

    def get_by_id(
        self,
        product_id: int
    ):

        try:

            product = (
                self.db.query(Product)
                .options(
                    joinedload(Product.category),
                    joinedload(Product.subcategory),
                    joinedload(Product.brand),
                    joinedload(Product.images),

                    joinedload(Product.variants)
                        .joinedload(ProductVariant.variant_values)
                        .joinedload(ProductVariantValue.attribute_value),

                    joinedload(Product.specifications)    
                )
                .filter(
                    Product.id == product_id,
                    Product.deleted_at.is_(None)
                )
                .first()
            )

            attribute_ids = set()
            attribute_value_ids = []

            for variant in product.variants:

                for variantValue in variant.variant_values:

                    attribute_value_ids.append(
                        variantValue.attribute_value_id
                    )

                    attribute_ids.add(
                        variantValue.attribute_value.attribute_id
                    )

            if not product:

                return {
                    "status": False,
                    "message": "Product not found.",
                    "data": None
                }

            data = {
                "id": product.id,
                "category_id": product.category_id,
                "subcategory_id": product.subcategory_id,
                "brand_id": product.brand_id,
                "name": product.name,
                "slug": product.slug,
                "sku": product.sku,
                "price": product.price,
                "stock": product.stock,
                "has_variant": product.has_variant,
                "attribute_ids": list(attribute_ids),
                "attribute_value_ids": attribute_value_ids,

                "variants": [
                    {
                        "id": variant.id,
                        "variant_value_ids": ",".join(
                            str(v.attribute_value_id)
                            for v in variant.variant_values
                        ),
                        "variant_name": " / ".join(
                            v.attribute_value.value
                            for v in variant.variant_values
                        ),
                        "sku": variant.sku,
                        "price": variant.price,
                        "stock": variant.stock,
                        "status": variant.status
                    }
                    for variant in product.variants
                ],

                "short_description": product.short_description,
                "description": product.description,
                "specifications": [
                    {
                        "title": specification.title,
                        "value": specification.value
                    }
                    for specification in product.specifications
                ],
                "main_image": product.main_image,
                "gallery_images": [
                    {
                        "id": image.id,
                        "image": image.image
                    }
                    for image in product.images
                ],
                "seo_title": product.seo_title,
                "meta_description":product.meta_description,
                "meta_keywords":product.meta_keywords,
                "tags": product.tags,
                "status": product.status,
                "approval_status": product.approval_status,
                "commission_type":product.commission_type,
                "commission_value":product.commission_value,
                "featured": product.is_featured,
                "created_at": product.created_at,
                "updated_at": product.updated_at
            }

            return {
                "status": True,
                "message": "Product fetched successfully.",
                "data": data
            }

        except Exception as e:

            return {
                "status": False,
                "message": str(e),
                "data": None
            }
        
    # Update Product By Id
    def update(self, product_id: int, product_data: ProductUpdate):

        product = (
            self.db.query(Product)
            .filter(Product.id == product_id)
            .first()
        )

        if not product:
            return None

        product.category_id = product_data.category_id
        product.subcategory_id = product_data.subcategory_id
        product.brand_id = product_data.brand_id
        product.name = product_data.name
        product.slug = product_data.slug
        product.sku = product_data.sku
        product.price = product_data.price
        product.stock = product_data.stock
        product.commission_type = product_data.commission_type
        product.commission_value = product_data.commission_value
        product.short_description = product_data.short_description
        product.description = product_data.description
        product.seo_title = product_data.seo_title
        product.meta_description = product_data.meta_description
        product.meta_keywords = product_data.meta_keywords
        product.tags = product_data.tags
        product.has_variant = product_data.has_variant
        product.status = product_data.status
        product.is_featured = product_data.is_featured
        # Main image update karenge
        product.main_image = product_data.main_image

        #self.db.commit()
        #self.db.refresh(product)

        return product
