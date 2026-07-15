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