from pydantic import BaseModel
from typing import Optional

class JobRequest(BaseModel):

    department: str

    job_description: str