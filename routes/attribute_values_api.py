import math
from fastapi import Body
from models.attribute_value import AttributeValue
from fastapi import (APIRouter, Depends, HTTPException, File, Form, Request)
from sqlalchemy.orm import Session
from config.database import get_db
from repositories.attribute_repository_value import AttributeValueRepository

router = APIRouter(prefix="/admin/attributesValue")


# Attribute Value Section Start
@router.post("/attributevalue/create")
async def create_attribute_value(
    request: Request,
    attribute_id: int = Form(...),
    value: str = Form(...),
    status: int = Form(1),
    db: Session = Depends(get_db)
):
    # Check Admin Authentication
    admin = getattr(request.state, "admin", None)
    if not admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Validation
    value = value.strip()

    if not value:
        return {
            "status": False,
            "message": "Attribute value is required."
        }

    # Save
    result = AttributeValueRepository().create(db, {
        "attribute_id": attribute_id,
        "value": value,
        "status": status
    })

    if not result["status"]:
        return result

    attributeValues = result["data"]

    return {
        "status": True,
        "message": result["message"],
        "data": [
            {
                "id": attributeValue.id,
                "attribute_id": attributeValue.attribute_id,
                "value": attributeValue.value,
                "status": attributeValue.status
            }
            for attributeValue in attributeValues
        ]
    }

# Attribute List
@router.get("/attributevalue/list")
def list_attribute_value(
    page: int = 1,
    limit: int = 10,
    search: str = None,
    attribute_id: int = None,
    status: str = None,
    db: Session = Depends(get_db)
):

    attribute_values, total = AttributeValueRepository().get_all(
        db=db,
        page=page,
        limit=limit,
        search=search,
        attribute_id=attribute_id,
        status=status
    )

    data = []

    for item in attribute_values:
        data.append({
            "id": item.id,
            "attribute_id": item.attribute_id,
            "attribute_name": item.attribute.name if item.attribute else "",
            "value": item.value,
            "status": item.status,
            "updated_at": item.updated_at.strftime("%d-%m-%Y %I:%M %p") if item.updated_at else ""
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


# Edit attribute Value By id
@router.get("/attributevalue/{attribute_value_id}")
def get_attribute_value(request: Request, attribute_value_id: int, db: Session = Depends(get_db)):

    admin = getattr(request.state, "admin", None)

    # 1. AUTH CHECK
    if not admin:
        raise HTTPException(status_code=403, detail="Not authorized")


    attributeValue = AttributeValueRepository().get_by_id(db, attribute_value_id)

    if not attributeValue:
        raise HTTPException(status_code=404, detail="Attribute Value not found")

    return {
        "status": True,
        "data": {
            "id": attributeValue.id,
            "attribute_id": attributeValue.attribute_id,
            "value": attributeValue.value,
            "status": attributeValue.status,
            "created_at": attributeValue.created_at.strftime("%d %b %Y %I:%M %p")
        }
    }

# Update attribute Value By id
@router.put("/attributevalue/update/{id}")
async def update_attribute_value(
    id: int,
    request: Request,
    attribute_id: int = Form(...),
    value: str = Form(...),
    status: int = Form(...),
    db: Session = Depends(get_db)
):
    admin = getattr(request.state, "admin", None)
    if not admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Validation
    value = value.strip()

    if not value:
        return {
            "status": False,
            "message": "Attribute value is required."
        }

    # Get Record
    attribute_value = AttributeValueRepository().get_by_id(db, id)

    if not attribute_value:
        return {
            "status": False,
            "message": "Attribute value not found."
        }

    # Update
    result = AttributeValueRepository().update(
        db,
        attribute_value,
        {
            "attribute_id": attribute_id,
            "value": value,
            "status": status
        }
    )

    return result

# Attribute value Single Delete
@router.delete("/attributevalue/delete/{id}")
def delete_attribute_value(
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
        result = AttributeValueRepository().delete(db, id)

        return result

    except Exception as e:
        return {
            "status": False,
            "message": str(e)
        }

# Attribute Value Bulk Deleted
@router.post("/attributevalue/bulk-delete-value")
def bulk_delete_attribute_value(request: Request,payload: dict,db: Session = Depends(get_db),):

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
    attributeValue = db.query(AttributeValue)\
        .filter(AttributeValue.id.in_(clean_ids),
                AttributeValue.deleted_at == None)\
        .all()

    if not attributeValue:
        raise HTTPException(status_code=404, detail="No Attribute Value found")

    # 5. SOFT DELETE (SAFE)
    db.query(AttributeValue)\
        .filter(AttributeValue.id.in_(clean_ids))\
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

