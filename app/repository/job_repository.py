from datetime import datetime

from bson import ObjectId

from app.repository.base_repository import BaseRepository


class JobRepository(BaseRepository):

    def __init__(self):

        super().__init__()

        self.collection = self.db["jobs"]

    # =====================================================
    # Create Job
    # =====================================================

    def create_job(
        self,
        job: dict,
        embedding: list,
        department: str,
        search_period: str,
    ):

        document = {

            "title": job.get("title", ""),

            "department": department,

            "job_description": job,

            "job_embedding": embedding,

            "search_period": search_period,

            "created_at": datetime.utcnow(),

            "updated_at": datetime.utcnow(),

            "status": "PROCESSING",

            "cached": False,

            "search_result_count": 0,

        }

        result = self.collection.insert_one(document)

        return str(result.inserted_id)

    # =====================================================
    # Update Job
    # =====================================================

    def update_job(
        self,
        job_id: str,
        update_fields: dict,
    ):

        update_fields["updated_at"] = datetime.utcnow()

        self.collection.update_one(
            {
                "_id": ObjectId(job_id)
            },
            {
                "$set": update_fields
            }
        )

    # =====================================================
    # Get Job
    # =====================================================

    def get_job(
        self,
        job_id: str,
    ):

        document = self.collection.find_one(
            {
                "_id": ObjectId(job_id)
            }
        )

        if not document:
            return None

        document["_id"] = str(document["_id"])

        # ---------------------------------------------
        # Flatten Parsed Job
        # ---------------------------------------------

        parsed_job = document.get(
            "job_description",
            {}
        )

        return {

            "job_id": document["_id"],

            "title": parsed_job.get(
                "title",
                ""
            ),

            "department": document.get(
                "department",
                ""
            ),

            "experience": parsed_job.get(
                "experience",
                ""
            ),

            "education": parsed_job.get(
                "education",
                ""
            ),

            "skills": parsed_job.get(
                "skills",
                []
            ),

            "certifications": parsed_job.get(
                "certifications",
                []
            ),

            "responsibilities": parsed_job.get(
                "responsibilities",
                []
            ),

            "qualifications": parsed_job.get(
                "qualifications",
                []
            ),

            "nice_to_have": parsed_job.get(
                "nice_to_have",
                []
            ),

            "status": document.get(
                "status"
            ),

            "created_at": document.get(
                "created_at"
            ),

        }

    # =====================================================
    # Get All Jobs
    # =====================================================

    def get_all_jobs(self):

        jobs = list(

            self.collection.find()

            .sort("created_at", -1)

        )

        for job in jobs:

            job["_id"] = str(job["_id"])

        return jobs

    # =====================================================
    # Delete Job
    # =====================================================

    def delete_job(
        self,
        job_id: str,
    ):

        self.collection.delete_one(
            {
                "_id": ObjectId(job_id)
            }
        )

    # =====================================================
    # Count Jobs
    # =====================================================

    def count_jobs(self):

        return self.collection.count_documents({})

    # =====================================================
    # Find Similar Job (Cache)
    # =====================================================

    def find_similar_job(
        self,
        embedding: list,
        department: str,
        threshold: float = 0.95,
    ):

        pipeline = [

            {
                "$vectorSearch": {

                    "index": "job_vector_index",

                    "path": "job_embedding",

                    "queryVector": embedding,

                    "numCandidates": 20,

                    "limit": 1,

                    "filter": {

                        "department": department

                    }

                }
            },

            {
                "$project": {

                    "_id": 1,

                    "title": 1,

                    "department": 1,

                    "score": {

                        "$meta": "vectorSearchScore"

                    }

                }
            }

        ]

        jobs = list(

            self.collection.aggregate(

                pipeline

            )

        )

        if not jobs:

            return None

        if jobs[0]["score"] < threshold:

            return None

        return jobs[0]

    # =====================================================
    # Mark Cached
    # =====================================================

    def mark_as_cached(
        self,
        job_id: str,
    ):

        self.collection.update_one(

            {

                "_id": ObjectId(job_id)

            },

            {

                "$set": {

                    "cached": True,

                    "updated_at": datetime.utcnow(),

                }

            }

        )

    # =====================================================
    # Update Result Count
    # =====================================================

    def update_result_count(
        self,
        job_id: str,
        count: int,
    ):

        self.collection.update_one(

            {

                "_id": ObjectId(job_id)

            },

            {

                "$set": {

                    "search_result_count": count,

                    "updated_at": datetime.utcnow(),

                }

            }

        )

    # =====================================================
    # Update Status
    # =====================================================

    def update_status(
        self,
        job_id: str,
        status: str,
    ):

        self.collection.update_one(

            {

                "_id": ObjectId(job_id)

            },

            {

                "$set": {

                    "status": status,

                    "updated_at": datetime.utcnow(),

                }

            }

        )

    # =====================================================
    # Get Processing Jobs
    # =====================================================

    def get_processing_jobs(self):

        jobs = list(

            self.collection.find(

                {

                    "status": "PROCESSING"

                }

            )

        )

        for job in jobs:

            job["_id"] = str(job["_id"])

        return jobs

    # =====================================================
    # Get Completed Jobs
    # =====================================================

    def get_completed_jobs(self):

        jobs = list(

            self.collection.find(

                {

                    "status": "COMPLETED"

                }

            ).sort(

                "created_at",

                -1,

            )

        )

        for job in jobs:

            job["_id"] = str(job["_id"])

        return jobs

    # =====================================================
    # Latest Job
    # =====================================================

    def get_latest_job(self):

        job = self.collection.find_one(

            sort=[

                ("created_at", -1)

            ]

        )

        if job:

            job["_id"] = str(job["_id"])

        return job