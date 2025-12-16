import json
from dotenv import load_dotenv
from sqlalchemy import select, desc
from src.db.session import SessionLocal
from src.db.models import CompanyDetails


def main(limit: int = 20):
    load_dotenv()
    with SessionLocal() as session:
        stmt = select(CompanyDetails).order_by(desc(CompanyDetails.id)).limit(limit)
        rows = session.execute(stmt).scalars().all()
        if not rows:
            print("No rows found in Company_details.")
            return
        for r in rows:
            try:
                founders = json.loads(r.founded_by)
            except Exception:
                founders = r.founded_by
            print(f"{r.id}\t{r.company_name}\t{r.founded_in}\t{founders}")


if __name__ == "__main__":
    main()