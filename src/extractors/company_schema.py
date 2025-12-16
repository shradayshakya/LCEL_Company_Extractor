from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class CompanyRecord(BaseModel):
    company_name: str = Field(...)
    founded_in: date = Field(...)
    founded_by: List[str] = Field(default_factory=list)

class ExtractionResult(BaseModel):
    records: List[CompanyRecord] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
