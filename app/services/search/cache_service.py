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

    # =====================================================
    # Find Similar Job
    # =====================================================

    def find_similar_job(
        self,
        embedding: list,
        department: str,
        threshold: float = 0.95,
    ):

        return self.job_repository.find_similar_job(
            embedding=embedding,
            department=department,
            threshold=threshold,
        )

    # =====================================================
    # Cache Exists
    # =====================================================

    def cache_exists(
        self,
        embedding: list,
        department: str,
    ) -> bool:

        job = self.find_similar_job(
            embedding=embedding,
            department=department,
        )

        return job is not None

    # =====================================================
    # Get Cached Job
    # =====================================================

    def get_cached_job(
        self,
        embedding: list,
        department: str,
    ):

        return self.find_similar_job(
            embedding=embedding,
            department=department,
        )

    # =====================================================
    # Mark Cached
    # =====================================================

    def mark_cached(
        self,
        job_id: str,
    ):

        self.job_repository.mark_as_cached(job_id)