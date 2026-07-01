from pydantic import BaseModel
from typing import Optional

class SearchRequest(BaseModel):

    department: str

    designation: str

    job_description: str

    search_period: str = "ALL"

    top_k: int = 20