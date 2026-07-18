from sqlalchemy.orm import joinedload
from models.attribute_value import AttributeValue
from models.attribute import Attribute
from datetime import datetime
from sqlalchemy import or_

class AttributeValueRepository:

    def get_all(self,db,page=1,limit=10,search=None,attribute_id=None,status=None):

        query = (
            db.query(AttributeValue)
            .join(Attribute)
            .options(joinedload(AttributeValue.attribute))
            .filter(AttributeValue.deleted_at == None)
        )

        if search:
            query = query.filter(
                or_(
                    AttributeValue.value.ilike(f"%{search}%"),
                    Attribute.name.ilike(f"%{search}%")
                )
            )

        # Attribute Filter
        if attribute_id:
            query = query.filter(
                AttributeValue.attribute_id == attribute_id
            )

        # Status Filter
        if status is not None and status != "":
            query = query.filter(
                AttributeValue.status == status
            )

        # Total Records
        total = query.count()

        # Pagination
        attribute_values = (
            query.order_by(AttributeValue.id.desc())
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )

        return attribute_values, total

    def get_by_attribute_and_value(self, db, attribute_id, value):
        return (
            db.query(AttributeValue)
            .filter(
                AttributeValue.attribute_id == attribute_id,
                AttributeValue.value == value,
                AttributeValue.deleted_at == None
            )
            .first()
        )

     # ---------------- GET BY ID ----------------
    
    def get_by_id(self, db, attribute_value_id):
        try:
            return (
                db.query(AttributeValue)
                .options(joinedload(AttributeValue.attribute))
                .filter(
                    AttributeValue.id == attribute_value_id,
                    AttributeValue.deleted_at == None
                )
                .first()
            )

        except Exception as e:
            return {
                "status": False,
                "message": str(e)
            }  


    def create(self, db, data):

        try:
            # Validate value
            if not data.get("value"):
                return {
                    "status": False,
                    "message": "Attribute value is required."
                }

            # Split comma separated values
            values = [
                v.strip()
                for v in data["value"].split(",")
                if v.strip()
            ]

            if not values:
                return {
                    "status": False,
                    "message": "Invalid attribute values."
                }

            created = []

            for value in values:

                # Duplicate Check
                existing = self.get_by_attribute_and_value(
                    db,
                    data["attribute_id"],
                    value
                )

                if existing:
                    continue

                attribute_value = AttributeValue(
                    attribute_id=data["attribute_id"],
                    value=value,
                    status=data.get("status", 1)
                )

                db.add(attribute_value)

                created.append(attribute_value)

            # All values duplicate
            if not created:
                return {
                    "status": False,
                    "message": "All attribute values already exist."
                }

            # Save
            db.commit()

            # Refresh IDs
            for item in created:
                db.refresh(item)

            return {
                "status": True,
                "message": f"{len(created)} Attribute Value(s) created successfully.",
                "data": created
            }

        except Exception as e:

            db.rollback()

            return {
                "status": False,
                "message": str(e)
            }
    
    def update(self, db, attribute_value, data):

        # Duplicate Check
        existing = (
            db.query(AttributeValue)
            .filter(
                AttributeValue.attribute_id == data["attribute_id"],
                AttributeValue.value == data["value"],
                AttributeValue.id != attribute_value.id,
                AttributeValue.deleted_at == None
            )
            .first()
        )

        if existing:
            return {
                "status": False,
                "message": "Attribute value already exists."
            }

        attribute_value.attribute_id = data["attribute_id"]
        attribute_value.value = data["value"]
        attribute_value.status = data["status"]

        db.commit()
        db.refresh(attribute_value)

        return {
            "status": True,
            "message": "Attribute value updated successfully.",
            "data": attribute_value
        }
    

    def delete(self, db, id):

        attribute_value = (
            db.query(AttributeValue)
            .filter(
                AttributeValue.id == id,
                AttributeValue.deleted_at == None
            )
            .first()
        )

        if not attribute_value:
            return {
                "status": False,
                "message": "Attribute Value not found."
            }

        attribute_value.deleted_at = datetime.utcnow()

        db.commit()

        return {
            "status": True,
            "message": "Attribute Value deleted successfully."
        }
    
    # Varient Section Start

    def get_by_attribute_ids(self, db, attribute_ids):
        return (
            db.query(AttributeValue)
            .options(joinedload(AttributeValue.attribute))
            .filter(AttributeValue.attribute_id.in_(attribute_ids))
            .filter(AttributeValue.status == 1)
            .order_by(AttributeValue.attribute_id)
            .all()
        )