from sqlalchemy.orm import Session
from models.admin import Admin

class AdminRepository:

    @staticmethod
    def get_by_email(db: Session, email: str):
        return db.query(Admin).filter(Admin.email == email).first()

    @staticmethod
    def get_by_id(db: Session, admin_id: int):
        return db.query(Admin).filter(Admin.id == admin_id).first()

    @staticmethod
    def update_last_login(db: Session, admin_id: int):
        admin = db.query(Admin).filter(Admin.id == admin_id).first()

        if admin:
            from datetime import datetime
            admin.last_login = datetime.now()
            db.commit()

        return admin