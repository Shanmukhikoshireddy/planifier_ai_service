from app.repository.job_repository import JobRepository


class CacheService:
    """
    Responsible for Job Cache.

    Determines whether a similar
    Job Description has already
    been processed.
    """

    def __init__(self):

        self.job_repository = JobRepository()

    # ==========================================
    # Find Similar Job
    # ==========================================

    def find_similar_job(

        self,

        embedding: list,

        department: str,

        designation: str,

        threshold: float = 0.95,

    ):

        return self.job_repository.find_similar_job(

            embedding=embedding,

            department=department,

            designation=designation,

            threshold=threshold,

        )

    # ==========================================
    # Cache Exists
    # ==========================================

    def cache_exists(

        self,

        embedding,

        department,

        designation,

    ) -> bool:

        job = self.find_similar_job(

            embedding,

            department,

            designation,

        )

        return job is not None

    # ==========================================
    # Get Cached Job
    # ==========================================

    def get_cached_job(

        self,

        embedding,

        department,

        designation,

    ):

        return self.find_similar_job(

            embedding,

            department,

            designation,

        )