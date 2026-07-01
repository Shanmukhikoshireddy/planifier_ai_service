from pathlib import Path
import shutil
import uuid
from fastapi import UploadFile
from app.config.logging import logger
from app.config.settings import settings
from app.repository.upload_repository import UploadRepository
from app.repository.minio_repository import MinioRepository
from app.workers.ingestion_worker import IngestionWorker
from app.services.ingestion.zip_service import ZipService
class IngestionService:
    """
    Resume Ingestion Workflow

    Responsibilities
    ----------------
    1. Validate Upload
    2. Extract ZIP
    3. Upload resumes to MinIO
    4. Create Upload Records
    5. Trigger Background Worker
    """
    def __init__(self):
        self.upload_repository = UploadRepository()
        self.minio_repository = MinioRepository()
        self.zip_service = ZipService()
        self.worker = IngestionWorker()
    # =====================================================
    # Upload Resume ZIP
    # =====================================================

    def upload_resumes(

        self,

        zip_file: UploadFile,

        department: str,

        designation: str,

        uploaded_by: str = "Recruiter",

    ):

        logger.info(

            "Resume Upload Started."

        )

        # ----------------------------------------

        upload_job_id = str(

            uuid.uuid4()

        )

        

        # ----------------------------------------

        upload_folder = Path(

            settings.UPLOAD_DIR

        )

        upload_folder.mkdir(

            parents=True,

            exist_ok=True,

        )

        # ----------------------------------------

        zip_path = upload_folder / f"{upload_job_id}.zip"

        with open(

            zip_path,

            "wb",

        ) as buffer:

            shutil.copyfileobj(

                zip_file.file,

                buffer,

            )

        logger.info(

            f"ZIP Saved : {zip_path}"

        )

        # ----------------------------------------

        extract_path = self.zip_service.extract(

            zip_path=str(zip_path),

            extract_to=str(

                Path(settings.EXTRACT_DIR)

                / upload_job_id

            ),

        )

        # ----------------------------------------

        resumes = self.zip_service.find_resumes(

            extract_path

        )

        if len(resumes) == 0:

            raise Exception(

                "No resumes found inside ZIP."

            )

        logger.info(

            f"Found {len(resumes)} resumes."

        )
       
        # Remaining workflow continues
        # in Part-2

        return self.process_uploaded_resumes(

            upload_job_id=upload_job_id,

            resumes=resumes,

            department=department,

            designation=designation,

            uploaded_by=uploaded_by,

        )
        # =====================================================
    # Process Uploaded Resumes
    # =====================================================

    def process_uploaded_resumes(

        self,

        upload_job_id: str,

        resumes: list,

        department: str,

        designation: str,

        uploaded_by: str,

    ):

        uploaded_count = 0

        for resume_path in resumes:

            resume_id = str(

                uuid.uuid4()

            )

            stored_file_name = (

                f"{resume_id}"

                f"{resume_path.suffix}"

            )

            minio_path = self.build_minio_path(

                department=department,

                designation=designation,

                upload_job_id=upload_job_id,

                stored_file_name=stored_file_name,

            )

            with open(

                resume_path,

                "rb",

            ) as file:

                file_bytes = file.read()

            self.minio_repository.upload_file(

                object_name=minio_path,

                data=file_bytes,

                content_type="application/pdf",

            )

            self.upload_repository.create_upload_record(

                upload_job_id=upload_job_id,

                resume_id=resume_id,

                department=department,

                designation=designation,

                original_file_name=resume_path.name,

                stored_file_name=stored_file_name,

                minio_path=minio_path,

                uploaded_by=uploaded_by,

            )

            uploaded_count += 1

            logger.info(

                f"{resume_path.name} uploaded."

            )

        logger.info(

            f"{uploaded_count} resumes uploaded to MinIO."

        )

        self.worker.process(upload_job_id)

        return {

            "message": "Resume upload started successfully.",

            "upload_job_id": upload_job_id,

            "total_resumes": uploaded_count,

            "status": "PROCESSING",

        }


    # =====================================================
    # Build MinIO Path
    # =====================================================

    def build_minio_path(

        self,

        department: str,

        designation: str,

        upload_job_id: str,

        stored_file_name: str,

    ) -> str:

        return (

            f"resumes/"

            f"{department}/"

            f"{designation}/"

            f"{upload_job_id}/"

            f"{stored_file_name}"

        )