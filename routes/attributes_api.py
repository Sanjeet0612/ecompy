import math
from fastapi import Body
from models.attribute import Attribute
from fastapi import (APIRouter, Depends, HTTPException, File, Form, Request)
from sqlalchemy.orm import Session
from config.database import get_db
from repositories.attribute_repository import AttributeRepository

router = APIRouter(prefix="/admin/attributes")

# Attribute Create
@router.post("/attribute/create")
async def create_attribute(
    request: Request,
    name: str = Form(...),
    status: int = Form(1),
    db: Session = Depends(get_db)
):
    admin = getattr(request.state, "admin", None)
    if not admin:
        raise HTTPException(status_code=403, detail="Not authorized")


    # Duplicate check
    existing = AttributeRepository().get_by_name(db, name)
    if existing:
        raise HTTPException(status_code=400, detail="Attribute already exists")


    attribute = AttributeRepository().create(db, {
            "name": name,
            "status": status
        })

    return {
        "status": True,
        "message": "Attribute created successfully.",
        "data": {
            "id": attribute.id,
            "name": attribute.name,
            "status": attribute.status
        }
    }
# Attribute List
@router.get("/attribute/list")
def list_attribute(
    page: int = 1,
    limit: int = 10,
    search: str = None,
    status: str = None,
    db: Session = Depends(get_db)
):

    attributes, total = AttributeRepository().get_all(
        db=db,
        page=page,
        limit=limit,
        search=search,
        status=status
    )

    data = []

    for item in attributes:
        data.append({
            "id": item.id,
            "name": item.name,
            "status": item.status,
            "updated_at": item.updated_at
        })

    pages = math.ceil(total / limit) if total > 0 else 1

    return {
        "status": True,
        "data": data,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages
    }

# Edit attribute By id
@router.get("/attribute/{attribute_id}")
def get_attribute(request: Request, attribute_id: int, db: Session = Depends(get_db)):

    admin = getattr(request.state, "admin", None)

    # 1. AUTH CHECK
    if not admin:
        raise HTTPException(status_code=403, detail="Not authorized")


    attribute = AttributeRepository().get_by_id(db, attribute_id)

    if not attribute:
        raise HTTPException(status_code=404, detail="Attribute not found")

    return {
        "status": True,
        "data": {
            "id": attribute.id,
            "name": attribute.name,
            "status": attribute.status,
            "created_at": attribute.created_at.strftime("%d %b %Y %I:%M %p")
        }
    }
# Update attribute By id
@router.put("/attribute/update/{attribute_id}")
async def update_attribute(
    request: Request,
    attribute_id: int,
    name: str = Form(...),
    status: int = Form(...),
    db: Session = Depends(get_db)
):

    admin = getattr(request.state, "admin", None)

    # 1. AUTH CHECK
    if not admin:
        raise HTTPException(status_code=403, detail="Not authorized")


    attribute = AttributeRepository().get_by_id(db, attribute_id)

    if not attribute:
        raise HTTPException(status_code=404, detail="Attribute not found")

    
    data = {
        "name": name,
        "status": status
    }

    attribute = AttributeRepository().update(db, attribute, data)

    return {
        "status": True,
        "message": "Attribute updated successfully",
        "data": {
            "id": attribute.id,
            "name": attribute.name,
            "status": attribute.status
           
        }
    }

# Attribute Single Delete
@router.delete("/attribute/delete/{id}")
def delete_attribute(
    request: Request,
    id: int,
    db: Session = Depends(get_db)
):

    try:
        # ---------------- AUTH CHECK ----------------
        admin = getattr(request.state, "admin", None)

        if not admin:
            raise HTTPException(status_code=403, detail="Not authorized")

        # ---------------- DELETE ----------------
        result = AttributeRepository().delete(db, id)

        return result

    except Exception as e:
        return {
            "status": False,
            "message": str(e)
        }

# Attribute Bulk Deleted
@router.post("/attribute/bulk-delete")
def bulk_delete_attribute(request: Request,payload: dict,db: Session = Depends(get_db),):

    admin = getattr(request.state, "admin", None)

    # 1. AUTH CHECK
    if not admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    # 2. GET IDS
    ids = payload.get("ids", [])

    if not ids or not isinstance(ids, list):
        raise HTTPException(status_code=400, detail="Invalid IDs")

    # 3. VALIDATE IDS (remove invalid values)
    clean_ids = []
    for i in ids:
        try:
            clean_ids.append(int(i))
        except:
            continue

    if not clean_ids:
        raise HTTPException(status_code=400, detail="No valid IDs found")

    # 4. CHECK EXISTING DATA
    attribute = db.query(Attribute)\
        .filter(Attribute.id.in_(clean_ids),
                Attribute.deleted_at == None)\
        .all()

    if not attribute:
        raise HTTPException(status_code=404, detail="No Attribute found")

    # 5. SOFT DELETE (SAFE)
    db.query(Attribute)\
        .filter(Attribute.id.in_(clean_ids))\
        .update(
            {
                "deleted_at": datetime.utcnow()
            },
            synchronize_session=False
        )

    db.commit()

    return {
        "status": True,
        "message": f"{len(clean_ids)} Attribute deleted successfully",
        "deleted_ids": clean_ids
    }
