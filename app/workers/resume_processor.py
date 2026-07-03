import uuid
from datetime import datetime
from pathlib import Path

from app.config.logging import logger
from app.config.settings import settings

from app.repository.minio_repository import MinioRepository
from app.repository.profile_repository import ProfileRepository
from app.repository.embedding_repository import EmbeddingRepository

from app.services.ingestion.parser_service import ParserService
from app.services.ingestion.embedding_service import EmbeddingService
from app.services.ingestion.duplicate_service import DuplicateService

from app.services.llm.resume_extractor_service import ResumeExtractorService

from app.utils.hash import generate_hash


class ResumeProcessor:
    """
    Responsible for processing a single resume uploaded to MinIO.

    Workflow

    MinIO
        │
        ▼
    Download Resume
        │
        ▼
    Parse Resume
        │
        ▼
    Duplicate Check
        │
        ▼
    Resume Extraction
        │
        ▼
    Generate Embedding
        │
        ▼
    Save Profile
        │
        ▼
    Save Embedding
    """

    def __init__(self):

        self.minio_repository = MinioRepository()

        self.profile_repository = ProfileRepository()

        self.embedding_repository = EmbeddingRepository()

        self.parser_service = ParserService()

        self.embedding_service = EmbeddingService()

        self.duplicate_service = DuplicateService()

        self.resume_extractor = ResumeExtractorService()

    # =====================================================
    # Process Resume
    # =====================================================

    def process_resume(

        self,

        object_name: str,

    ):

        """
        Process one resume uploaded to MinIO.
        """

        logger.info("=" * 80)

        logger.info(

            f"Processing Resume : {object_name}"

        )

        logger.info("=" * 80)

        local_resume = None

        try:

            # -----------------------------------------

            # Generate Resume ID

            # -----------------------------------------

            resume_id = str(

                uuid.uuid4()

            )

            # -----------------------------------------

            # Download Resume

            # -----------------------------------------

            local_resume = self._download_resume(

                object_name

            )

            # -----------------------------------------

            # Parse Resume

            # -----------------------------------------

            parsed_resume = self._parse_resume(

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

            # Duplicate Validation

            # -----------------------------------------

            self._check_duplicate(

                file_hash

            )

            # -----------------------------------------

            # Extract Resume

            # -----------------------------------------

            structured_resume = self._extract_resume(

                raw_text

            )

            structured_resume["file_hash"] = file_hash

            structured_resume["raw_text"] = raw_text

            structured_resume["file_name"] = Path(

                object_name

            ).name

            # -----------------------------------------

            # Generate Embedding

            # -----------------------------------------

            embedding = self._generate_embedding(

                structured_resume

            )

            # -----------------------------------------

            # Save Profile

            # -----------------------------------------

            self._save_profile(

                resume_id=resume_id,

                resume=structured_resume,

                resume_path=object_name,
                file_hash=file_hash,


            )

            # -----------------------------------------

            # Save Embedding

            # -----------------------------------------

            self._save_embedding(

                resume_id=resume_id,

                embedding=embedding,

                department=structured_resume.get(

                    "department",

                    "Unknown",

                ),

            )

            logger.info(

                f"Resume Processed Successfully : {object_name}"

            )

        except ValueError as e:

            logger.warning(

                str(e)

            )

        except Exception as e:

            logger.exception(e)

        finally:

            self._cleanup(

                local_resume

            )


        # =====================================================
    # Download Resume From MinIO
    # =====================================================

    def _download_resume(
        self,
        object_name: str,
    ) -> Path:

        logger.info(
            "Downloading resume from MinIO..."
        )

        resume_bytes = self.minio_repository.download_file(
            object_name
        )

        temp_dir = Path(settings.TEMP_DIR)

        temp_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        local_file = temp_dir / Path(object_name).name

        with open(
            local_file,
            "wb",
        ) as file:

            file.write(
                resume_bytes
            )

        logger.info(
            f"Resume downloaded : {local_file.name}"
        )

        return local_file

    # =====================================================
    # Parse Resume
    # =====================================================

    def _parse_resume(
        self,
        resume_path: Path,
    ) -> dict:

        logger.info(
            "Parsing resume..."
        )

        parsed_resume = self.parser_service.parse_resume(
            resume_path
        )

        logger.info(
            "Resume parsed successfully."
        )

        return parsed_resume

    # =====================================================
    # Duplicate Validation
    # =====================================================

    def _check_duplicate(
        self,
        file_hash: str,
    ):

        logger.info(
            "Checking duplicate..."
        )

        self.duplicate_service.validate(
            file_hash
        )

        logger.info(
            "Duplicate check completed."
        )

    # =====================================================
    # Resume Extraction
    # =====================================================

    def _extract_resume(
        self,
        raw_text: str,
    ) -> dict:

        logger.info(
            "Extracting structured resume..."
        )

        resume = self.resume_extractor.extract_resume(
            raw_text
        )

        logger.info(
            "Resume extracted."
        )

        return resume

    # =====================================================
    # Generate Embedding
    # =====================================================

    def _generate_embedding(
        self,
        resume: dict,
    ) -> list:

        logger.info(
            "Preparing embedding text..."
        )

        embedding_text = self.resume_extractor.build_embedding_text(
            resume
        )

        logger.info(
            "Generating embedding..."
        )

        embedding = self.embedding_service.generate_embedding(
            embedding_text
        )

        logger.info(
            "Embedding generated."
        )

        return embedding
    

        # =====================================================
    # Save Candidate Profile
    # =====================================================

    def _save_profile(
        self,
        resume_id: str,
        resume: dict,
        resume_path: str,
        file_hash: str,
    ):

        logger.info(
            "Saving candidate profile..."
        )

        self.profile_repository.save_profile(
            resume_id=resume_id,
            resume=resume,
            resume_path=resume_path,
            file_hash=file_hash,
        )

        logger.info(
            "Candidate profile saved."
        )

    # =====================================================
    # Save Embedding
    # =====================================================

    def _save_embedding(
        self,
        resume_id: str,
        embedding: list,
        department: str,
    ):

        logger.info(
            "Saving embedding..."
        )

        self.embedding_repository.save_embedding(
            resume_id=resume_id,
            embedding=embedding,
            embedding_model=settings.EMBEDDING_MODEL,
            dimension=len(embedding),
            department=department,
            uploaded_at=datetime.utcnow(),
        )

        logger.info(
            "Embedding saved."
        )

    # =====================================================
    # Cleanup Temporary File
    # =====================================================

    def _cleanup(
        self,
        local_resume: Path | None,
    ):

        if local_resume is None:

            return

        try:

            if local_resume.exists():

                local_resume.unlink()

                logger.info(
                    f"Temporary file deleted : {local_resume.name}"
                )

        except Exception as e:

            logger.exception(e)