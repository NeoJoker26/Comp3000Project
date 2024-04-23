from sqlalchemy import Float, String
from sqlalchemy.orm import Mapped, mapped_column
from base import Base

"""
This is the file to create the table, i use "banana quality" as a concept (as shown in the comment below) however, 
also as mentioned, this can be anything, here is an example different structures:

id: Mapped[int] = mapped_column(primary_key=True)
name: Mapped[str] = mapped_column(String(100))
employees: Mapped[list["Employee"]] = relationship(back_populates="department")

department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"))
department: Mapped["Department"] = relationship(back_populates="employees")

where this would apply to 2 tables (department and employees)

id: Mapped[int] = mapped_column(primary_key=True)
name: Mapped[str] = mapped_column(String(100))
role: Mapped[str] = mapped_column(Enum("admin", "user", "guest", name="user_roles"))

where this would apply to sysadmin/user/guest roles/tables

id: Mapped[int] = mapped_column(primary_key=True)
name: Mapped[str] = mapped_column(String(100), index=True)
category: Mapped[str] = mapped_column(String(50))
price: Mapped[float] = mapped_column(Float)

__table_args__ = (
    Index("idx_product_category", "category"),
    )
where this would apply for a product catalog or something of the sort
"""
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
