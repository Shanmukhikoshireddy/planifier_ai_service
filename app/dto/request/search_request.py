from pydantic import BaseModel

class SearchRequest(BaseModel):
    job_position: str
    job_description: str
    received_within: str = "ALL"

    # page: int = 1
    # page_size: int = 20