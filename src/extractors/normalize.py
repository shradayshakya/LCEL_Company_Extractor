from typing import Optional
from datetime import date
import dateparser

MONTH_DEFAULT_DAY = 1


def normalize_date(raw: str) -> Optional[date]:
    if not raw:
        return None
    dt = dateparser.parse(raw, settings={"PREFER_DAY_OF_MONTH": "first"})
    if dt:
        # If only year present, dateparser returns Jan 1; If year+month, returns 1st.
        return dt.date()
    # Try year only
    try:
        year = int(raw)
        return date(year, 1, 1)
    except Exception:
        return None
