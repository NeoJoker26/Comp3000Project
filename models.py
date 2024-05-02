import datetime

from sqlalchemy import Float, String, func, DateTime
from sqlalchemy.ext.hybrid import hybrid_property
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

    @hybrid_property
    def masked_quality(self):
        return func.concat('X' * (func.length(self.quality) - 2), func.substr(self.quality, -2, 2))

    @masked_quality.expression
    def masked_quality(cls):
        return func.concat('X' * (func.length(cls.quality) - 2), func.substr(cls.quality, -2, 2))

    def __repr__(self):
        # represent the obj as a string
        return f"Banana(banana_id={self.banana_id!r}, size={self.size!r}, weight={self.weight!r}, sweetness={self.sweetness!r}, softness={self.softness!r}, harvest_time={self.harvest_time!r}, ripeness={self.ripeness!r}, acidity={self.acidity!r}, quality={self.quality!r})"


class RDM(Base):
    __tablename__ = 'rdm'

    id: Mapped[int] = mapped_column(primary_key=True)
    service_name: Mapped[str] = mapped_column(String(100), nullable=False)
    ip_address: Mapped[str] = mapped_column(String(50), nullable=False)
    port: Mapped[int] = mapped_column(nullable=False)
    service_type: Mapped[str] = mapped_column(String(50), nullable=False)
    resource_availability: Mapped[str] = mapped_column(String(100), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<RDM(id={self.id}, service_name='{self.service_name}', ip_address='{self.ip_address}', port={self.port}, service_type='{self.service_type}', resource_availability='{self.resource_availability}', timestamp='{self.timestamp}')>"