from pydantic import BaseModel
from typing import Optional


class UploadRequest(BaseModel):

    department: str

    designation: str

    uploaded_by: Optional[str] = "Recruiter"