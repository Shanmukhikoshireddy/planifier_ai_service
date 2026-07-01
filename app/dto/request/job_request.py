from pydantic import BaseModel
from typing import Optional

class JobRequest(BaseModel):

    department: str

    designation: str

    job_description: str