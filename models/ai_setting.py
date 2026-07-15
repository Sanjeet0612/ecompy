from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Text,
    Enum,
    DECIMAL,
    Integer,
    SmallInteger,
    DateTime,
    func,
)

from config.database import Base


class AISetting(Base):
    __tablename__ = "ai_settings"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    provider = Column(
        Enum("gemini", "openai", "claude", "grok"),
        nullable=False,
        default="gemini"
    )

    model = Column(
        String(100),
        nullable=False
    )

    temperature = Column(
        DECIMAL(3, 2),
        nullable=False,
        default=0.70
    )

    top_p = Column(
        DECIMAL(3, 2),
        nullable=False,
        default=0.95
    )

    max_output_tokens = Column(
        Integer,
        nullable=False,
        default=8192
    )

    language = Column(
        String(20),
        nullable=False,
        default="English"
    )

    description_length = Column(
        Enum("short", "medium", "long"),
        nullable=False,
        default="medium"
    )

    generate_seo = Column(
        SmallInteger,
        nullable=False,
        default=1
    )

    generate_tags = Column(
        SmallInteger,
        nullable=False,
        default=1
    )

    generate_specifications = Column(
        SmallInteger,
        nullable=False,
        default=1
    )

    system_prompt = Column(
        Text,
        nullable=True
    )

    status = Column(
        SmallInteger,
        nullable=False,
        default=1
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )

    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )