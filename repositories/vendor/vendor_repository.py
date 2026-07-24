from sqlalchemy.orm import Session

from models.vendor.vendor import Vendor


class VendorRepository:

    @staticmethod
    def get_by_email(db: Session, email: str):
        return db.query(Vendor).filter(
            Vendor.email == email,
            Vendor.deleted_at == None
        ).first()


    @staticmethod
    def create(db: Session, vendor: Vendor):
        db.add(vendor)
        db.flush()
        db.refresh(vendor)
        return vendor

    @staticmethod
    def get_by_verification_token(db: Session, token: str):
        return db.query(Vendor).filter(
            Vendor.email_verification_token == token,
            Vendor.deleted_at == None
        ).first()

    @staticmethod
    def update(db: Session, vendor: Vendor):
        db.add(vendor)
        db.flush()
        db.refresh(vendor)
        return vendor