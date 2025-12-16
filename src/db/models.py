from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Date

class Base(DeclarativeBase):
    pass

class CompanyDetails(Base):
    __tablename__ = "Company_details"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    founded_in: Mapped[Date] = mapped_column(Date, nullable=False)
    founded_by: Mapped[str] = mapped_column(String(1024), nullable=False)  # JSON string list
