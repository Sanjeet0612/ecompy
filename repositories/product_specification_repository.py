import json
from sqlalchemy.orm import Session

from models.product_specification import ProductSpecification


class ProductSpecificationRepository:

    def create(
        self,
        db: Session,
        product_id: int,
        title: str,
        value: str,
        sort_order: int = 0
    ):

        specification = ProductSpecification(
            product_id=product_id,
            title=title,
            value=value,
            sort_order=sort_order
        )

        db.add(specification)

        return specification


    def delete_by_product(
        self,
        db: Session,
        product_id: int
    ):

        db.query(ProductSpecification).filter(
            ProductSpecification.product_id == product_id
        ).delete()

        db.flush()


    def save_specifications(
        self,
        db: Session,
        product_id: int,
        specifications: str
    ):

        specifications_list = []

        if specifications:
            try:
                specifications_list = json.loads(specifications)
            except json.JSONDecodeError:
                specifications_list = []

        for index, specification in enumerate(specifications_list):

            title = specification.get("title", "").strip()
            value = specification.get("value", "").strip()

            if not title or not value:
                continue

            self.create(
                db=db,
                product_id=product_id,
                title=title,
                value=value,
                sort_order=index + 1
            )