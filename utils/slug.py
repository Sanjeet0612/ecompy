from slugify import slugify
from sqlalchemy.orm import Session


def generate_unique_slug(
    db: Session,
    model,
    name: str,
    current_id: int = None
) -> str:

    base_slug = slugify(name)

    slug = base_slug

    counter = 2

    while True:

        query = db.query(model).filter(model.slug == slug)

        if current_id:

            query = query.filter(model.id != current_id)

        exists = query.first()

        if not exists:
            return slug

        slug = f"{base_slug}-{counter}"

        counter += 1