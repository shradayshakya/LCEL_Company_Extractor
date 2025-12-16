import json
from typing import List
from sqlalchemy.orm import Session
from ..db.session import SessionLocal, engine
from ..db.models import Base, CompanyDetails

class DbInsertTool:
    name = "db_insert_company_details"
    description = "Insert company details into PostgreSQL"

    def __init__(self):
        Base.metadata.create_all(bind=engine)

    def run(self, company_name: str, founded_in, founded_by: List[str]):
        with SessionLocal() as session:  # type: Session
            record = CompanyDetails(
                company_name=company_name,
                founded_in=founded_in,
                founded_by=json.dumps(founded_by),
            )
            session.add(record)
            session.commit()
