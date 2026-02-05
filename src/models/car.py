from sqlalchemy import String, Integer, DateTime, func, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase


class Base(DeclarativeBase):
    pass


class Car(Base):
    __tablename__ = "cars"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    url: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    title: Mapped[str | None] = mapped_column(String, nullable=True)
    price_usd: Mapped[int | None] = mapped_column(Integer, nullable=True)
    odometer: Mapped[int | None] = mapped_column(Integer, nullable=True)
    username: Mapped[str | None] = mapped_column(String, nullable=True)
    phone_number: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    image_url: Mapped[str | None] = mapped_column(String, nullable=True)
    images_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    car_number: Mapped[str | None] = mapped_column(String, nullable=True)
    car_vin: Mapped[str | None] = mapped_column(String, nullable=True)
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())