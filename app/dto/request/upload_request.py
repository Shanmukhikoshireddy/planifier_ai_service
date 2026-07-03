from pydantic import BaseModel
from typing import Optional


class UploadRequest(BaseModel):

    department: str


    uploaded_by: Optional[str] = "Recruiter"