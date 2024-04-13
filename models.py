from sqlalchemy import Column, Integer, Float, String
from sqlalchemy.orm import Mapped, mapped_column
from base import Base


class Banana(Base):
    # the table name, but this can be anything as it is a concept
    __tablename__ = "banana_quality"

    # the columns in the db
    banana_id: Mapped[int] = mapped_column(primary_key=True)
    size: Mapped[float] = mapped_column(Float)
    weight: Mapped[float] = mapped_column(Float)
    sweetness: Mapped[float] = mapped_column(Float)
    softness: Mapped[float] = mapped_column(Float)
    harvest_time: Mapped[float] = mapped_column(Float)
    ripeness: Mapped[float] = mapped_column(Float)
    acidity: Mapped[float] = mapped_column(Float)
    quality: Mapped[str] = mapped_column(String(10))

    def __repr__(self):
        # represent the obj as a string
        return f"Banana(banana_id={self.banana_id!r}, size={self.size!r}, weight={self.weight!r}, sweetness={self.sweetness!r}, softness={self.softness!r}, harvest_time={self.harvest_time!r}, ripeness={self.ripeness!r}, acidity={self.acidity!r}, quality={self.quality!r})"
