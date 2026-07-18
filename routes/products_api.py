import json
from fastapi import Body
from models.product import Product
from fastapi import (APIRouter, Depends, HTTPException, UploadFile, File, Form, Request)
from sqlalchemy.orm import Session
from config.database import get_db
from repositories.attribute_repository_value import AttributeValueRepository
from repositories.ai_setting_repository import aiSettingRepository
from repositories.product_repository import ProductRepository
from repositories.product_specification_repository import ProductSpecificationRepository
from repositories.product_variant_repository import ProductVariantRepository
from schemas.product import ProductCreate, ProductUpdate
from sqlalchemy.exc import IntegrityError
from schemas.product import BulkDeleteRequest
from utils.slug import generate_unique_slug
from utils.file_upload import (upload_image,delete_image,PRODUCT_MAIN_PATH,PRODUCT_GALLERY_PATH)
from typing import Optional

router = APIRouter(prefix="/admin/products")


#-------------------------Product Varient Section Start---------------------------------------

@router.post("/product/get-attribute-values")
async def get_attribute_values(
    request: Request,
    payload: dict = Body(...),
    db: Session = Depends(get_db)
):

    attribute_ids = payload.get("attribute_ids", [])

    values = AttributeValueRepository().get_by_attribute_ids(
        db,
        attribute_ids
    )

    data = []

    for value in values:

        data.append({
            "id": value.id,
            "attribute_id": value.attribute_id,
            "attribute_name": value.attribute.name,
            "value": value.value
        })

    return {
        "status": True,
        "data": data
    }


#-----------------------Product List, Save Section start---------------------------

# Product List
@router.get("/product/list")
def list_product(
    page: int = 1,
    limit: int = 10,
    search: str = "",
    status: str = "",
    category_id: Optional[int] = None,
    subcategory_id: Optional[int] = None,
    db: Session = Depends(get_db)
):

    try:
        repository = ProductRepository(db)
        result = repository.get_all(
            db=db,
            page=page,
            limit=limit,
            search=search,
            status=status,
            category_id=category_id,
            subcategory_id=subcategory_id
        )

        return {
            "status": True,
            "message": "Products fetched successfully.",
            "data": result["data"],
            "total": result["total"],
            "page": page,
            "limit": limit
        }

    except Exception as e:

        return {
            "status": False,
            "message": str(e),
            "data": [],
            "total": 0,
            "page": page,
            "limit": limit
        }
# Save Product
@router.post("/product/create")
async def create_product(
    request: Request,
    category_id: int = Form(...),
    subcategory_id: int = Form(...),
    brand_id: int = Form(...),
    productName: str = Form(...),
    short_description: str = Form(None),
    description: str = Form(None),
    specifications: str = Form(""),
    has_variant: int = Form(...),
    sku: str = Form(None),
    price: float = Form(0),
    stock: int = Form(0),
    commission_type: str = Form("percentage"),
    commission_value: float = Form(0),
    seo_title: str = Form(None),
    meta_description: str = Form(None),
    meta_keywords: str = Form(None),
    tags : str = Form(None),
    status: int = Form(1),
    featured:int=Form(0),
    variant_value_ids: Optional[list[str]] = Form(None, alias="variant_value_ids[]"),
    variant_names: Optional[list[str]] = Form(None, alias="variant_names[]"),
    variant_sku: Optional[list[str]] = Form(None, alias="variant_sku[]"),
    variant_price: Optional[list[float]] = Form(None, alias="variant_price[]"),
    variant_stock: Optional[list[int]] = Form(None, alias="variant_stock[]"),
    variant_status: Optional[list[int]] = Form(None, alias="variant_status[]"),
    main_image: UploadFile = File(None),
    gallery_images: list[UploadFile] = File(alias="gallery_images[]"),
    
    db: Session = Depends(get_db)
):

    admin = getattr(request.state, "admin", None)

    if not admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    slug = generate_unique_slug(db=db,model=Product,name=productName)
    
    # Main Image Section 
    main_image_name = None

    if main_image:
        main_image_name = await upload_image(
            main_image,
            PRODUCT_MAIN_PATH
        )
    # Gallery Section
    gallery_image_names = []
    
    for image in gallery_images:
        if image.filename:
            filename = await upload_image(
                image,
                PRODUCT_GALLERY_PATH
            )
            gallery_image_names.append(filename)

    
    try:

        product_data = ProductCreate(
            vendor_id=0,
            category_id=category_id,
            subcategory_id=subcategory_id,
            brand_id=brand_id,
            name=productName,
            slug=slug,
            sku=sku,
            price=price,
            stock=stock,
            commission_type=commission_type,
            commission_value=commission_value,
            short_description=short_description,
            description=description,
            seo_title=seo_title,
            meta_description = meta_description,
            meta_keywords = meta_keywords,
            tags = tags,
            main_image=main_image_name,
            has_variant=has_variant,
            status=status,
            is_featured=featured
        )

        product_repository = ProductRepository(db)
        product = product_repository.create(product_data)
        product_repository.save_gallery_images(product.id,gallery_image_names)

        # Variant Section

        variants = []

        if has_variant == 1:

            for i in range(len(variant_sku)):

                variants.append({
                    "attribute_value_ids": [
                        int(x)
                        for x in variant_value_ids[i].split(",")
                    ],
                    "sku": variant_sku[i],
                    "price": variant_price[i],
                    "stock": variant_stock[i],
                    "status": variant_status[i]
                })

            variant_data = product_repository.save_variants(product.id,variants)

            product_repository.save_variant_values(variant_data)

        # Specification    
        productSpecificationRepository = ProductSpecificationRepository()

        productSpecificationRepository.save_specifications(
            db=db,
            product_id=product.id,
            specifications=specifications
        )

        db.commit()

        return {
            "status": True,
            "message": "Product created successfully.",
            "data": {
                "id": product.id
            }
        }

    except IntegrityError as e:

        db.rollback()

        if "slug" in str(e.orig):

            return {
                "status": False,
                "message": "A product with this name already exists. Please use a different product name."
            }

        return {
            "status": False,
            "message": "Duplicate data found."
        }

# Update Product
@router.post("/product/update/{product_id}")
async def update_product(
    product_id: int,
    request: Request,
    category_id: int = Form(...),
    subcategory_id: int = Form(...),
    brand_id: int = Form(...),
    productName: str = Form(...),
    short_description: str = Form(None),
    description: str = Form(None),
    specifications: str = Form(""),
    has_variant: int = Form(...),
    sku: str = Form(None),
    price: float = Form(0),
    stock: int = Form(0),
    commission_type: str = Form("percentage"),
    commission_value: float = Form(0),
    seo_title: str = Form(None),
    meta_description: str = Form(None),
    meta_keywords: str = Form(None),
    tags: str = Form(None),
    status: int = Form(1),
    featured: int = Form(0),
    variant_value_ids: Optional[list[str]] = Form(None, alias="variant_value_ids[]"),
    variant_names: Optional[list[str]] = Form(None, alias="variant_names[]"),
    variant_sku: Optional[list[str]] = Form(None, alias="variant_sku[]"),
    variant_price: Optional[list[float]] = Form(None, alias="variant_price[]"),
    variant_stock: Optional[list[int]] = Form(None, alias="variant_stock[]"),
    variant_status: Optional[list[int]] = Form(None, alias="variant_status[]"),
    main_image: UploadFile = File(None),
    gallery_images: Optional[list[UploadFile]] = File(default=None,alias="gallery_images[]"),
    deleted_gallery_ids: Optional[list[int]] = Form(default=None,alias="deleted_gallery_ids[]"),
    db: Session = Depends(get_db)
):
    
    admin = getattr(request.state, "admin", None)

    if not admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    product_repository = ProductRepository(db)
    existing_product = product_repository.get_by_id(product_id)

    if not existing_product:
        return {
            "status": False,
            "message": "Product not found."
        }

    product_data = existing_product["data"]
    slug = product_data["slug"]
    #name = product_data["name"]
            

    # Main Image Section 
    product_info = existing_product["data"]
    old_main_image = product_info["main_image"]
    main_image_name = old_main_image

    # Upload new image only if selected
    if main_image and main_image.filename:
        main_image_name = await upload_image(
            main_image,
            PRODUCT_MAIN_PATH
        )

    # Gallery Section
    gallery_image_names = []

    for image in (gallery_images or []):
        if image.filename:
            filename = await upload_image(
                image,
                PRODUCT_GALLERY_PATH
            )
            gallery_image_names.append(filename)

    try:

        product_data = ProductUpdate(
            vendor_id=0,
            category_id=category_id,
            subcategory_id=subcategory_id,
            brand_id=brand_id,
            name=productName,
            slug=slug,
            sku=sku,
            price=price,
            stock=stock,
            commission_type=commission_type,
            commission_value=commission_value,
            short_description=short_description,
            description=description,
            seo_title=seo_title,
            meta_description = meta_description,
            meta_keywords = meta_keywords,
            tags = tags,
            main_image=main_image_name,
            has_variant=has_variant,
            status=status,
            is_featured=featured
        )

        product_repository = ProductRepository(db)
        product = product_repository.update(
            product_id=product_id,
            product_data=product_data
        )

        if not product:
            return {
                "status": False,
                "message": "Product not found."
            }
        
        # Delete old image only after successful update
        if (
            main_image
            and main_image.filename
            and old_main_image
            and old_main_image != main_image_name
        ):
            delete_image(old_main_image)
  

        # Delete selected gallery images
        if deleted_gallery_ids:
            for image_id in deleted_gallery_ids:
                gallery_image = product_repository.delete_gallery_image(image_id)

                if gallery_image:
                    delete_image(gallery_image.image)

        # Save new gallery images
        if gallery_image_names:
            product_repository.save_gallery_images(
                product.id,
                gallery_image_names
            )

        productSpecificationRepository = ProductSpecificationRepository()

        productSpecificationRepository.delete_by_product(
            db=db,
            product_id=product.id
        )
        
        productSpecificationRepository.save_specifications(
            db=db,
            product_id=product.id,
            specifications=specifications
        )

        # Variant Section Start

        productVariantRepository = ProductVariantRepository(db)

        # Delete old variants
        productVariantRepository.delete_by_product(
            product_id=product.id
        )

        # Save new variants
        if (
            has_variant == 1
            and variant_value_ids
            and variant_sku
        ):

            productVariantRepository.save_variants(
                product_id=product.id,
                variant_value_ids=variant_value_ids,
                variant_sku=variant_sku,
                variant_price=variant_price,
                variant_stock=variant_stock,
                variant_status=variant_status
            )

        db.commit()
        db.refresh(product)
        
        return {
            "status": True,
            "message": "Product Updated successfully.",
            "data": {
                "id": product.id
            }
        }

    except IntegrityError as e:

        db.rollback()
        error = str(e.orig).lower()

        if "slug" in error:

            return {
                "status": False,
                "message": "A product with this name already exists. Please choose a different product name."
            }

        elif "sku" in error:

            return {
                "status": False,
                "message": "This SKU already exists. Please use a unique SKU."
            }

        return {
            "status": False,
            "message": "A duplicate record already exists."
        }

# Get Product By Id
@router.get("/product/{product_id}")
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):

    try:

        productRepository = ProductRepository(db)

        result = productRepository.get_by_id(
            product_id=product_id
        )

        return result

    except Exception as e:

        return {
            "status": False,
            "message": str(e),
            "data": None
        }

# Delete By Id
@router.delete("/product/delete/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db)
):

    try:
        productRepository = ProductRepository(db)
        result = productRepository.delete(
            db=db,
            product_id=product_id
        )

        return result

    except Exception as e:

        return {
            "status": False,
            "message": str(e)
        }      
# Bulk Delete
@router.post("/product/bulk-delete")
def bulk_delete_products(
    request: BulkDeleteRequest,
    db: Session = Depends(get_db)
):

    try:

        productRepository = ProductRepository(db)

        result = productRepository.bulk_delete(
            product_ids=request.product_ids
        )

        return result

    except Exception as e:

        return {
            "status": False,
            "message": str(e)
        }

