import os, uuid, re
from fastapi import Body
from models.blog import Blog
from fastapi import (APIRouter, Depends, HTTPException, UploadFile, File, Form, Request)
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from repositories.blog_repository import BlogRepository
from schemas.blog import BlogCreate, BlogUpdate
from utils.slug import generate_unique_slug
from config.database import get_db
from utils.file_upload import (upload_image,delete_image,BLOG_MAIN_PATH)

router = APIRouter(prefix="/admin/blog")


# Blog List
@router.get("/list")
def list_blog(
    page: int = 1,
    limit: int = 10,
    search: str = "",
    status: str = "",
    db: Session = Depends(get_db)
):

    try:
        repository = BlogRepository(db)
        result = repository.get_all(
            db=db,
            page=page,
            limit=limit,
            search=search,
            status=status
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

#Blog Create
@router.post("/create")
async def add_blog(
    request: Request,
    category_id: int = Form(...),
    title: str = Form(...),
    short_description: str = Form(None),
    description: str = Form(None),
    seo_title: str = Form(None),
    meta_description: str = Form(None),
    meta_keywords: str = Form(None),
    tags : str = Form(None),
    status: int = Form(1),
    main_image: UploadFile = File(None),
    db: Session = Depends(get_db)
    
):
    admin = getattr(request.state, "admin", None)

    if not admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    

    slug = generate_unique_slug(db=db,model=Blog,name=title)

    # Main Image Section 
    main_image_name = None

    if main_image:
        main_image_name = await upload_image(
            main_image,
            BLOG_MAIN_PATH
        )

    try:

        blog_data = BlogCreate(
            
            category_id=category_id,
            title=title,
            slug=slug,
            short_description=short_description,
            description=description,
            seo_title=seo_title,
            meta_description = meta_description,
            meta_keywords = meta_keywords,
            tags = tags,
            featured_image=main_image_name,
            status=status,
           
        )

        blog_repository = BlogRepository(db)
        product = blog_repository.create(blog_data)

        db.commit()

        return {
            "status": True,
            "message": "Blog created successfully.",
            "data": {
                "id": product.id
            }
        } 
    
    except IntegrityError as e:

        db.rollback()

        if "slug" in str(e.orig):

            return {
                "status": False,
                "message": "A blog with this title already exists. Please use a different blog title."
            }

        return {
            "status": False,
            "message": "Duplicate data found."
        }
    
# Get Blog By Id
@router.get("/blog/{blog_id}")
def get_product(
    blog_id: int,
    db: Session = Depends(get_db)
):

    try:

        blogRepository = BlogRepository(db)

        result = blogRepository.get_by_id(
            blog_id=blog_id
        )

        return result

    except Exception as e:

        return {
            "status": False,
            "message": str(e),
            "data": None
        }

# Update Blog

@router.post("/update/{blog_id}")
async def update_product(
    blog_id: int,
    request: Request,
    category_id: int = Form(...),
    title: str = Form(...),
    short_description: str = Form(None),
    description: str = Form(None),
    seo_title: str = Form(None),
    meta_description: str = Form(None),
    meta_keywords: str = Form(None),
    tags: str = Form(None),
    status: int = Form(1),
    featured_image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    
    admin = getattr(request.state, "admin", None)

    if not admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    blog_repository = BlogRepository(db)
    existing_blog = blog_repository.get_by_id(blog_id)

    if not existing_blog:
        return {
            "status": False,
            "message": "Product not found."
        }

    blog_data = existing_blog["data"]
    slug = blog_data["slug"]
    #name = product_data["name"]
            

    # Main Image Section 
    blog_info = existing_blog["data"]
    old_featured_image = blog_info["featured_image"]
    featured_image_name = old_featured_image

    # Upload new image only if selected
    if featured_image and featured_image.filename:
        featured_image_name = await upload_image(
            featured_image,
            BLOG_MAIN_PATH
        )

    try:

        blog_data = BlogUpdate(
            category_id=category_id,
            title=title,
            slug=slug,
            short_description=short_description,
            description=description,
            seo_title=seo_title,
            meta_description = meta_description,
            meta_keywords = meta_keywords,
            tags = tags,
            featured_image=featured_image_name,
            status=status
        )

        blog_repository = BlogRepository(db)
        blog = blog_repository.update(
            blog_id=blog_id,
            blog_data=blog_data
        )

        if not blog:
            return {
                "status": False,
                "message": "Blog not found."
            }
        
        # Delete old image only after successful update
        if (
            featured_image
            and featured_image.filename
            and old_featured_image
            and old_featured_image != featured_image_name
        ):
            delete_image(old_featured_image)
  
        db.commit()
        db.refresh(blog)
        
        return {
            "status": True,
            "message": "Blog Updated successfully.",
            "data": {
                "id": blog.id
            }
        }

    except IntegrityError as e:

        db.rollback()
        error = str(e.orig).lower()

        if "slug" in error:

            return {
                "status": False,
                "message": "A blog with this title already exists. Please choose a different blog title."
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
