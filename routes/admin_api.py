from fastapi import (APIRouter, Depends, HTTPException, Response, Form)
from sqlalchemy.orm import Session
from config.database import get_db
from repositories.admin_repository import AdminRepository
from repositories.category_repository import CategoryRepository
from repositories.sub_category_repository import SubCategoryRepository
from repositories.ai_setting_repository import aiSettingRepository
from schemas.admin import AdminLogin
from utils.security import verify_password
from utils.jwt import create_access_token
import utils.ai.gemini as gemini


router = APIRouter(prefix="/admin")

# Login section Start
@router.post("/api/login")
def admin_login(
    data: AdminLogin,
    response: Response,
    db: Session = Depends(get_db)
):

    admin = AdminRepository.get_by_email(db, data.email)

    if not admin or not verify_password(data.password, admin.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if admin.status == 0:
        raise HTTPException(status_code=403, detail="Your account is inactive")

    token = create_access_token({
        "admin_id": admin.id,
        "email": admin.email,
        "role": admin.role,
        "type": "admin"
    })

    response.set_cookie(
        key="admin_token",
        value=token,
        httponly=True,
        samesite="lax",
        path="/"
    )

    return {
        "status": True,
        "message": "Login successful",
        "token": token,
        "admin": {
            "id": admin.id,
            "name": admin.name,
            "email": admin.email,
            "role": admin.role
        }
    }

#--------------------------AI SETTING SECTION-----------------------------------------

# AI Setting List
@router.get("/aisetting/list")
def list_ai_setting(
    db: Session = Depends(get_db)
):
    try:

        setting = aiSettingRepository.get_settings(db)

        if not setting:
            return {
                "status": False,
                "message": "AI settings not found.",
                "data": None
            }

        return {
            "status": True,
            "message": "AI settings fetched successfully.",
            "data": {
                "id": setting.id,
                "provider": setting.provider,
                "model": setting.model,
                "temperature": float(setting.temperature),
                "top_p": float(setting.top_p),
                "max_output_tokens": setting.max_output_tokens,
                "language": setting.language,
                "description_length": setting.description_length,
                "generate_seo": setting.generate_seo,
                "generate_tags": setting.generate_tags,
                "generate_specifications": setting.generate_specifications,
                "system_prompt": setting.system_prompt,
                "status": setting.status
            }
        }

    except Exception as e:

        return {
            "status": False,
            "message": str(e)
        }

# Update AI Settings
@router.post("/aisetting/update")
def update_ai_setting(
    provider: str = Form(...),
    model: str = Form(...),
    temperature: float = Form(...),
    top_p: float = Form(...),
    max_output_tokens: int = Form(...),
    language: str = Form(...),
    description_length: str = Form(...),
    generate_seo: int = Form(...),
    generate_tags: int = Form(...),
    generate_specifications: int = Form(...),
    system_prompt: str = Form(""),
    status: int = Form(...),
    db: Session = Depends(get_db)
):

    try:

        aiSetting = aiSettingRepository.get_settings(db)

        if not aiSetting:

            return {
                "status": False,
                "message": "AI settings not found."
            }

        data = {
            "provider": provider,
            "model": model,
            "temperature": temperature,
            "top_p": top_p,
            "max_output_tokens": max_output_tokens,
            "language": language,
            "description_length": description_length,
            "generate_seo": generate_seo,
            "generate_tags": generate_tags,
            "generate_specifications": generate_specifications,
            "system_prompt": system_prompt,
            "status": status
        }

        aiSettingRepository.update_settings(
            db=db,
            settings=aiSetting,
            data=data
        )

        return {
            "status": True,
            "message": "AI settings updated successfully."
        }

    except Exception as e:

        db.rollback()

        return {
            "status": False,
            "message": str(e)
        }    

#-----------------------GIMINI GENERATE CONTENT Section start---------------------------

@router.post("/generate-content")
async def generate_content(
    product_name: str = Form(...),
    category: str = Form(""),
    sub_category: str = Form(""),
    brand: str = Form(""),
    features: str = Form(""),
    db: Session = Depends(get_db)
):
    settings = aiSettingRepository.get_settings(db)

    result = gemini.generate_product_content(
        product_name=product_name,
        category=category,
        sub_category =sub_category,
        brand=brand,
        features=features,
        settings=settings
    )

    if result.get("status") is False:
        return result

    return {
        "status": True,
        "message": "Content generated successfully.",
        "data": result
    }


# -------------------------Logout Section Start---------------------------------------
@router.post("/api/logout")
def logout(response: Response):
    response.delete_cookie("admin_token")
    return {
        "status": True,
        "message": "Logout successful"
    }

# -------------------------Common Section Start---------------------------------------

# Category Dropdown
@router.get("/categoryDropdown/dropdown")
def category_dropdown(
    db: Session = Depends(get_db)
):

    try:
        catrepository = CategoryRepository()
        data = catrepository.get_dropdown(db)

        return {
            "status": True,
            "message": "Categories fetched successfully.",
            "data": data
        }

    except Exception as e:

        return {
            "status": False,
            "message": str(e),
            "data": []
        }
    

# Sub Category Dropdown
@router.get("/subcategoryDropDown/dropdown")
def subcategory_dropdown(
    category_id: int,
    db: Session = Depends(get_db)
):

    try:
        subCategoryRepository = SubCategoryRepository()
        data = subCategoryRepository.get_dropdown_by_category(
            db=db,
            category_id=category_id
        )

        return {
            "status": True,
            "message": "Sub categories fetched successfully.",
            "data": data
        }

    except Exception as e:

        return {
            "status": False,
            "message": str(e),
            "data": []
        }    

