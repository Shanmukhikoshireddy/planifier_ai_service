from pathlib import Path
import shutil
import zipfile

from app.config.logging import logger


class ZipService:
    """
    Responsible only for ZIP extraction.

    Does NOT:
        • Upload to MinIO
        • Parse resumes
        • Save MongoDB
    """

    # =====================================================
    # Extract ZIP
    # =====================================================

    def extract(

        self,

        zip_path: str,

        extract_to: str,

    ) -> Path:

        extract_path = Path(

            extract_to

        )

        if extract_path.exists():

            shutil.rmtree(

                extract_path

            )

        extract_path.mkdir(

            parents=True,

            exist_ok=True,

        )

        logger.info(

            f"Extracting : {zip_path}"

        )

        with zipfile.ZipFile(

            zip_path,

            "r",

        ) as zip_ref:

            zip_ref.extractall(

                extract_path

            )

        logger.info(

            f"Extraction Completed : {extract_path}"

        )

        return extract_path

    # =====================================================
    # Find PDFs
    # =====================================================

    def find_resumes(

        self,

        folder: Path,

    ) -> list[Path]:

        resumes = []

        for extension in (

            "*.pdf",

            "*.docx",

        ):

            resumes.extend(

                folder.rglob(

                    extension

                )

            )

        logger.info(

            f"Found {len(resumes)} resumes."

        )

        return resumes

    # =====================================================
    # Delete Temporary Folder
    # =====================================================

    def cleanup(

        self,

        folder: str,

    ):

        folder = Path(

            folder

        )

        if folder.exists():

            shutil.rmtree(

                folder

            )

            logger.info(

                f"Deleted Temp Folder : {folder}"

            )