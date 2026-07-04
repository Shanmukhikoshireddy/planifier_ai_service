from fastapi import APIRouter
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from io import BytesIO
from app.repository.profile_repository import ProfileRepository
from app.repository.minio_repository import MinioRepository

router = APIRouter(
    prefix="/api/cv-service/resume",
    tags=["Resume"],
)
profile_repository = ProfileRepository()
minio_repository = MinioRepository()

# Get Resume Profile
@router.get("/{resume_id}",)
def get_resume(resume_id: str,):
    profile = profile_repository.get_profile(resume_id)
    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Resume not found.",
        )
    return profile


# List All Resumes
@router.get("/",)
def get_resumes():
    return profile_repository.get_all_profiles()


# Download Resume
@router.get("/download/{resume_id}",)
def download_resume(resume_id: str,):
    profile = profile_repository.get_profile(resume_id)
    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Resume not found.",
        )

    pdf = minio_repository.download_file(profile["resume_path"])
    return StreamingResponse(
        BytesIO(pdf),
        media_type="application/pdf",
        headers={
            "Content-Disposition":
            f'attachment; filename="{resume_id}.pdf"'
        },
    )

# Soft Delete Resume
@router.delete("/{resume_id}",)

def delete_resume(resume_id: str,):
    updated = profile_repository.soft_delete_profile(
        resume_id
    )
    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Resume not found.",
        )
    return {
        "message": "Resume deleted successfully."
    }