from models.attribute import Attribute
from datetime import datetime

class AttributeRepository:

    def create(self, db, data):
        attribute = Attribute(**data)
        db.add(attribute)
        db.commit()
        db.refresh(attribute)
        return attribute
    
    def get_all(self, db, page=1, limit=10, search=None, status=None):
        query = db.query(Attribute).filter(Attribute.deleted_at == None)

        # Search
        if search:
            query = query.filter(Attribute.name.like(f"%{search}%"))

        # Status Filter
        if status is not None and status != "":
            query = query.filter(Attribute.status == status)

        # Total Records
        total = query.count()

        # Pagination
        attributes = (
            query.order_by(Attribute.id.desc())
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )

        return attributes, total
    

    def get_by_id(self, db, attribute_id):
        return (
            db.query(Attribute)
            .filter(
                Attribute.id == attribute_id,
                Attribute.deleted_at == None
            )
            .first()
        )
    
    def get_by_name(self, db, name):
        return (
            db.query(Attribute)
            .filter(
                Attribute.name == name,
                Attribute.deleted_at == None
            )
            .first()
        )
    
    
     # ---------------- GET BY Slug ----------------
     
    def get_by_slug(self, db, slug):
        return db.query(Attribute).filter(Attribute.slug == slug).first()


    def update(self, db, attribute, data):
        attribute.name = data["name"]
        attribute.status = data["status"]
        db.commit()
        db.refresh(attribute)
        return attribute
    

    def get_active_attributes(self, db):
        return (
            db.query(Attribute)
            .filter(
                Attribute.status == 1,
                Attribute.deleted_at == None
            )
            .order_by(Attribute.name.asc())
            .all()
        )


    # ---------------- DELETE ----------------
    def delete(self, db, attribute_id):
        try:

            attribute = db.query(Attribute).filter(
                Attribute.id == attribute_id,
                Attribute.deleted_at == None
            ).first()

            if not attribute:
                return {
                    "status": False,
                    "message": "Attribute not found"
                }

            attribute.deleted_at = datetime.utcnow()

            db.commit()

            return {
                "status": True,
                "message": "Attribute deleted successfully"
            }

        except Exception as e:
            db.rollback()

            return {
                "status": False,
                "message": str(e)
            }