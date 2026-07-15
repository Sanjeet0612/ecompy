from sqlalchemy.orm import Session

from models.ai_setting import AISetting


class AISettingRepository:

    def get_settings(self, db: Session):

        return (
            db.query(AISetting)
            .filter(AISetting.status == 1)
            .first()
        )

    def update_settings(self, db: Session, settings: AISetting, data: dict):

        for key, value in data.items():

            setattr(settings, key, value)

        db.commit()

        db.refresh(settings)

        return settings


aiSettingRepository = AISettingRepository()