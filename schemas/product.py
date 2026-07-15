from pydantic import BaseModel
from typing import Optional


# =========================================
# CREATE PRODUCT
# =========================================

class ProductCreate(BaseModel):
    vendor_id: int
    category_id: int
    subcategory_id: int
    brand_id: int
    name: str
    slug: str
    sku: Optional[str] = None
    price: Optional[float] = 0
    stock: Optional[int] = 0
    commission_type: Optional[str] = "percentage"
    commission_value: Optional[float] = 0
    short_description: Optional[str] = None
    description: Optional[str] = None
    seo_title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None
    tags: Optional[str] = None
    main_image: Optional[str] = None
    has_variant: int = 0
    status: int = 1
    


# =========================================
# UPDATE PRODUCT
# =========================================

class ProductUpdate(BaseModel):
    category_id: int
    subcategory_id: int
    brand_id: int

    name: str
    slug: str

    sku: Optional[str] = None
    price: Optional[float] = 0
    stock: Optional[int] = 0

    short_description: Optional[str] = None
    description: Optional[str] = None
    seo_title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None
    tags: Optional[str] = None

    main_image: Optional[str] = None
    has_variant: int = 0

    status: int = 1


# =========================================
# PRODUCT LIST RESPONSE
# =========================================

class ProductListResponse(BaseModel):
    id: int

    name: str
    slug: str

    main_image: Optional[str] = None

    has_variant: int

    status: int
    approval_status: int
    product_state: int

    class Config:
        from_attributes = True


# =========================================
# PRODUCT DETAIL RESPONSE
# =========================================

class ProductDetailResponse(BaseModel):
    id: int
    vendor_id: int
    category_id: int
    subcategory_id: int
    brand_id: int
    name: str
    slug: str
    short_description: Optional[str] = None
    description: Optional[str] = None
    seo_title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None
    tags: Optional[str] = None
    main_image: Optional[str] = None
    has_variant: int
    status: int
    approval_status: int
    product_state: int
    is_featured: int
    sort_order: int

    class Config:
        from_attributes = True