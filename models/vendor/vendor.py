from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, text
from sqlalchemy.sql import func
from config.database import Base


class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)
    shop_name = Column(String(150), nullable=False)

    email = Column(String(150), unique=True, nullable=False, index=True)
    phone = Column(String(20), unique=True, nullable=False)

    password = Column(String(255), nullable=False)

    logo = Column(String(255), nullable=True)
    banner = Column(String(255), nullable=True)

    gst_number = Column(String(50), nullable=True)
    pan_number = Column(String(20), nullable=True)

    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    pincode = Column(String(20), nullable=True)

    description = Column(Text, nullable=True)

    status = Column(Integer, default=1)
    email_verified = Column(Integer, default=0)

    email_verification_token = Column(String(255), nullable=True)
    email_verification_expiry = Column(TIMESTAMP, nullable=True)

    created_at = Column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP")
    )

    updated_at = Column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP"),
        server_onupdate=text("CURRENT_TIMESTAMP")
    )

    deleted_at = Column(TIMESTAMP, nullable=True)