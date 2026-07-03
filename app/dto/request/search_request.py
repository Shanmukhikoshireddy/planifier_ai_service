from pydantic import BaseModel

class SearchRequest(BaseModel):

    department: str

    job_description: str

    search_period: str = "ALL"

    page: int = 1

    page_size: int = 20