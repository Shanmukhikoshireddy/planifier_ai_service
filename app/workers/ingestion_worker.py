from app.repository.upload_repository import UploadRepository
from app.repository.profile_repository import ProfileRepository
from app.repository.embedding_repository import EmbeddingRepository
from app.repository.minio_repository import MinioRepository

from app.services.ingestion.parser_service import ParserService
from app.services.ingestion.embedding_service import EmbeddingService
from app.services.ingestion.duplicate_service import DuplicateService

from app.services.shared.openai_service import OpenAIService

from app.prompts.resume_prompt import build_resume_prompt

from app.utils.hash import generate_hash
from datetime import datetime
from app.config.logging import logger
from pathlib import Path
import traceback
class IngestionWorker:

    def __init__(self):

        self.upload_repository = UploadRepository()

        self.profile_repository = ProfileRepository()

        self.embedding_repository = EmbeddingRepository()

        self.minio_repository = MinioRepository()

        self.parser_service = ParserService()

        self.embedding_service = EmbeddingService()

        self.duplicate_service = DuplicateService()

        self.openai_service = OpenAIService()

    def process(

    self,

    upload_job_id: str,

):
        

        uploads = self.upload_repository.get_pending_uploads(

            upload_job_id

        )

        logger.info(

            f"Found {len(uploads)} pending resumes."

        )

        for upload in uploads:

            self.process_resume(

                upload

            )

    def process_resume(

    self,

    upload,

):
            try:

                # -----------------------------------------
                # Update Status
                # -----------------------------------------

                self.upload_repository.update_upload_status(

                    resume_id=upload["resume_id"],

                    status="PROCESSING",

                )

                logger.info(

                    f"Processing : {upload['original_file_name']}"

                )

                # -----------------------------------------
                # Download Resume From MinIO
                # -----------------------------------------

                pdf_bytes = self.minio_repository.download_file(

                    upload["minio_path"]

                )

                temp_path = Path("temp")

                temp_path.mkdir(

                    exist_ok=True,

                )

                local_resume = temp_path / upload["stored_file_name"]

                with open(

                    local_resume,

                    "wb",

                ) as file:

                    file.write(

                        pdf_bytes

                    )

                # -----------------------------------------
                # Parse Resume
                # -----------------------------------------

                parsed_resume = self.parser_service.parse_resume(

                    local_resume

                )

                raw_text = parsed_resume["raw_text"]

                # -----------------------------------------
                # Generate File Hash
                # -----------------------------------------

                file_hash = generate_hash(

                    raw_text

                )

                # -----------------------------------------
                # Duplicate Check
                # -----------------------------------------

                if self.duplicate_service.is_duplicate(

                    file_hash

                ):

                    logger.info(

                        "Duplicate Resume."

                    )

                    self.upload_repository.update_upload_status(

                        resume_id=upload["resume_id"],

                        status="DUPLICATE",

                    )

                    return

                # -----------------------------------------
                # OpenAI Resume Extraction
                # -----------------------------------------

                prompt = build_resume_prompt(

                    raw_text

                )

                structured_resume = self.openai_service.generate_json(

                    prompt

                )

                structured_resume["file_hash"] = file_hash

                structured_resume["raw_text"] = raw_text

                structured_resume["file_name"] = upload[
                    "original_file_name"
                ]


                # -----------------------------------------
                # Build Embedding Text
                # -----------------------------------------

                embedding_text = f"""
        Candidate:
        {structured_resume.get("candidate_name", "")}

        Experience:
        {structured_resume.get("total_experience", "")}

        Skills:
        {' '.join(structured_resume.get("skills", []))}

        Education:
        {
        chr(10).join(
        [
            f"{e.get('degree','')} {e.get('specialization','')} {e.get('institution','')}"
            for e in structured_resume.get("education", [])
        ]
        )
        }

        Projects:
        {
        chr(10).join(
        [
            f"{p.get('title','')} {p.get('description','')}"
            for p in structured_resume.get("projects", [])
        ]
        )
        }
        """

                # -----------------------------------------
                # Generate Embedding
                # -----------------------------------------

                embedding = self.embedding_service.generate_embedding(

                    embedding_text

                )
                
                # -----------------------------------------
                # Save Candidate Profile
                # -----------------------------------------

                self.profile_repository.save_profile(

                    resume_id=upload["resume_id"],

                    resume=structured_resume,

                    department=upload["department"],


                    resume_path=upload["minio_path"],

                )

                # -----------------------------------------
                # Save Embedding
                # -----------------------------------------

                self.embedding_repository.save_embedding(

                    resume_id=upload["resume_id"],

                    upload_job_id=upload["upload_job_id"],

                    embedding=embedding,

                    embedding_model="bge-m3",

                    dimension=len(embedding),

                    department=upload["department"],

                    uploaded_at=datetime.utcnow(),

                )

                # -----------------------------------------
                # Update Upload Status
                # -----------------------------------------

                self.upload_repository.update_upload_status(

                    resume_id=upload["resume_id"],

                    status="COMPLETED",

                )

                logger.info(

                    f"Completed : {upload['original_file_name']}"

                )

                # -----------------------------------------
                # Cleanup
                # -----------------------------------------

                if local_resume.exists():

                    local_resume.unlink()

            except Exception as e:

                logger.exception(e)

                self.upload_repository.update_upload_status(

                    resume_id=upload["resume_id"],

                    status="FAILED",

                    error=str(e),

                )

                if "local_resume" in locals():

                    if local_resume.exists():

                        local_resume.unlink()