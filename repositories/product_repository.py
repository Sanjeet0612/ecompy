from sqlalchemy.orm import Session

from models.product import Product
from schemas.product_schema import ProductCreate


class ProductRepository:

    def __init__(self, db: Session):
        self.db = db