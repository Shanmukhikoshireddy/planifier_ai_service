from datetime import datetime

from bson import ObjectId

from app.repository.base_repository import BaseRepository


class JobRepository(BaseRepository):

    def __init__(self):

        super().__init__()

        self.collection = self.db[
            "jobs"
        ]

    # =====================================================
    # Create Job
    # =====================================================

    def create_job(

        self,

        job,

        embedding,

        department: str,

        designation: str,

        search_period: str,

    ):

        document = {

            "title": job.title,

            "department": department,

            "designation": designation,

            "job_description": job,

            "job_embedding": embedding,

            "search_period": search_period,

            "created_at": datetime.utcnow(),

            "status": "PROCESSING",

            "cached": False,

            "search_result_count": 0,

        }

        result = self.collection.insert_one(

            document

        )

        return str(

            result.inserted_id

        )

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

        return self.collection.find_one(

            {

                "_id": ObjectId(job_id)

            },

            {

                "_id": 0

            }

        )

    # =====================================================
    # Get All Jobs
    # =====================================================

    def get_all_jobs(

        self,

    ):

        return list(

            self.collection.find(

                {},

                {

                    "_id": 0

                }

            ).sort(

                "created_at",

                -1,

            )

        )

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

    def count_jobs(

        self,

    ):

        return self.collection.count_documents(

            {}

        )

    # =====================================================
    # Find Similar Job (Cache)
    # =====================================================

    def find_similar_job(

        self,

        embedding: list,

        department: str,

        designation: str,

        threshold: float = 0.95,

    ):

        pipeline = [

            {

                "$vectorSearch": {

                    "index": "job_vector_index",

                    "path": "job_embedding",

                    "queryVector": embedding,

                    "numCandidates": 10,

                    "limit": 1,

                    "filter": {

                        "department": department,

                        "designation": designation,

                    }

                }

            },

            {

                "$project": {

                    "_id": 1,

                    "title": 1,

                    "department": 1,

                    "designation": 1,

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
    # Update Cache Flag
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

                    "cached": True

                }

            }

        )

    # =====================================================
    # Update Search Result Count
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

                    "search_result_count": count

                }

            }

        )

    # =====================================================
    # Update Job Status
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

                    "status": status

                }

            }

        )