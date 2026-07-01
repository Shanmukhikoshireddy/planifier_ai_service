from datetime import datetime
from typing import Optional

from bson import ObjectId

from app.repository.base_repository import BaseRepository


class UploadRepository(BaseRepository):

    def __init__(self):

        super().__init__()

        self.collection = self.db[
            "resume_uploads"
        ]

    # =====================================================
    # Create Upload Record
    # =====================================================

    def create_upload_record(

        self,

        upload_job_id: str,

        resume_id: str,

        department: str,

        designation: str,

        original_file_name: str,

        stored_file_name: str,

        minio_path: str,

        uploaded_by: str = "Recruiter",

    ):

        document = {

            "upload_job_id": upload_job_id,

            "resume_id": resume_id,

            "department": department,

            "designation": designation,

            "original_file_name": original_file_name,

            "stored_file_name": stored_file_name,

            "minio_path": minio_path,

            "uploaded_by": uploaded_by,

            "uploaded_at": datetime.utcnow(),

            "status": "PROCESSING",

            "error": None,

        }

        self.collection.insert_one(

            document

        )

    # =====================================================
    # Update Upload Status
    # =====================================================

    def update_upload_status(

        self,

        resume_id: str,

        status: str,

        error: Optional[str] = None,

    ):

        update = {

            "status": status,

        }

        if error:

            update["error"] = error

        self.collection.update_one(

            {

                "resume_id": resume_id

            },

            {

                "$set": update

            }

        )

    # =====================================================
    # Get Upload
    # =====================================================

    def get_upload(self, resume_id: str):

        document = self.collection.find_one(
            {"resume_id": resume_id}
        )

        if not document:
            return None

        document["_id"] = str(document["_id"])

        return document

    # =====================================================
    # Get All Uploads
    # =====================================================

    def get_all_uploads(

        self,

    ):

        return list(

            self.collection.find(

                {},

                {

                    "_id": 0

                }

            )

        )

    # =====================================================
    # Pending Uploads
    # =====================================================

    def get_pending_uploads(

        self,

        upload_job_id: str,

    ):

        return list(

            self.collection.find(

                {

                    "upload_job_id": upload_job_id,

                    "status": "PROCESSING",

                },

                {

                    "_id": 0

                }

            )

        )

    # =====================================================
    # Upload Progress
    # =====================================================

    def get_upload_progress(

        self,

        upload_job_id: str,

    ):

        total = self.collection.count_documents(

            {

                "upload_job_id": upload_job_id

            }

        )

        completed = self.collection.count_documents(

            {

                "upload_job_id": upload_job_id,

                "status": "COMPLETED",

            }

        )

        processing = self.collection.count_documents(

            {

                "upload_job_id": upload_job_id,

                "status": "PROCESSING",

            }

        )

        failed = self.collection.count_documents(

            {

                "upload_job_id": upload_job_id,

                "status": "FAILED",

            }

        )

        duplicate = self.collection.count_documents(

            {

                "upload_job_id": upload_job_id,

                "status": "DUPLICATE",

            }

        )

        processed = (

            completed

            + failed

            + duplicate

        )

        progress = 0

        if total > 0:

            progress = round(

                (processed / total) * 100,

                2,

            )

        is_completed = (

            total > 0

            and

            processed == total

        )

        return {

            "upload_job_id": upload_job_id,

            "total": total,

            "completed": completed,

            "processing": processing,

            "failed": failed,

            "duplicate": duplicate,

            "progress": progress,

            "is_completed": is_completed,

        }

    # =====================================================
    # Delete Upload
    # =====================================================

    def delete_upload(

        self,

        resume_id: str,

    ):

        self.collection.delete_one(

            {

                "resume_id": resume_id

            }

        )

    # =====================================================
    # Utility
    # =====================================================

    @staticmethod
    def to_object_id(

        value: str,

    ):

        return ObjectId(

            value

        )