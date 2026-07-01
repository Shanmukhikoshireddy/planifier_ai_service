from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import File
from fastapi import Form
from fastapi import HTTPException

from app.services.ingestion.ingestion_service import IngestionService
from app.repository.upload_repository import UploadRepository


router = APIRouter(

    prefix="/cv-service/resumes",

    tags=["Resume Ingestion"],

)

ingestion_service = IngestionService()
upload_repository = UploadRepository()


# =====================================================
# Upload Resume ZIP
# =====================================================

@router.post(

    "/upload",

)

async def upload_resumes(

    zip_file: UploadFile = File(...),

    department: str = Form(...),

    designation: str = Form(...),

    uploaded_by: str = Form("Recruiter"),

):

    try:

        if not zip_file.filename.lower().endswith(

            ".zip"

        ):

            raise HTTPException(

                status_code=400,

                detail="Only ZIP files are allowed.",

            )

        return ingestion_service.upload_resumes(

            zip_file=zip_file,

            department=department,

            designation=designation,

            uploaded_by=uploaded_by,

        )

    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=str(e),

        )
    
# =====================================================
# Upload Progress
# =====================================================

@router.get(

    "/checkuploadprocess/{upload_job_id}",

)

def check_upload_progress(

    upload_job_id: str,

):

    progress = upload_repository.get_upload_progress(

        upload_job_id

    )

    if progress is None:

        raise HTTPException(

            status_code=404,

            detail="Upload Job Not Found.",

        )

    return progress
# =====================================================
# Upload Details
# =====================================================

@router.get(

    "/upload/{resume_id}",

)

def get_upload(

    resume_id: str,

):

    upload = upload_repository.get_upload(

        resume_id

    )

    if upload is None:

        raise HTTPException(

            status_code=404,

            detail="Resume not found.",

        )

    return upload
# =====================================================
# List Uploads
# =====================================================

@router.get(

    "/uploads",

)

def get_uploads():

    return upload_repository.get_all_uploads()

# =====================================================
# Delete Upload
# =====================================================

@router.delete(

    "/upload/{resume_id}",

)

def delete_upload(

    resume_id: str,

):

    upload_repository.delete_upload(

        resume_id

    )

    return {

        "message": "Upload deleted successfully."

    }
