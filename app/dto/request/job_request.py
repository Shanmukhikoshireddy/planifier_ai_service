from pydantic import BaseModel
from typing import Optional

class JobRequest(BaseModel):

    job_position: str

    job_description: str