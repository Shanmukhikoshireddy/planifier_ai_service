from app.config.logging import logger

from app.repository.job_repository import JobRepository
from app.repository.search_repository import SearchRepository
from app.repository.embedding_repository import EmbeddingRepository
from app.repository.profile_repository import ProfileRepository

from app.services.shared.openai_service import OpenAIService

from app.services.ingestion.embedding_service import EmbeddingService

from app.services.search.cache_service import CacheService
from app.services.search.reranker_service import RerankerService
from app.services.search.scoring_service import ScoringService

from app.prompts.job_prompt import build_job_prompt
from app.prompts.reasoning_prompt import build_reasoning_prompt


class SearchService:

    """
    Complete Candidate Search Workflow.
    """

    def __init__(self):

        self.job_repository = JobRepository()

        self.search_repository = SearchRepository()

        self.embedding_repository = EmbeddingRepository()

        self.profile_repository = ProfileRepository()

        self.openai_service = OpenAIService()

        self.embedding_service = EmbeddingService()

        self.cache_service = CacheService()

        self.reranker_service = RerankerService()

        self.scoring_service = ScoringService()


        # =====================================================
    # Search Candidates
    # =====================================================

    def search(

        self,

        department: str,

        designation: str,

        job_description: str,

        top_k: int = 20,

    ):

        logger.info(

            "Starting Candidate Search."

        )

        # --------------------------------------

        prompt = build_job_prompt(

            job_description

        )

        job = self.openai_service.generate_json(

            prompt

        )

        logger.info(

            "Job Parsed Successfully."

        )

        # Remaining implementation
        # Part-2

        return self.process_job(

            job,

            department,

            designation,

            top_k,

            job_description,

        )
    
        # =====================================================
    # Build Job Text
    # =====================================================

    def build_job_embedding_text(

        self,

        job,

    ):

            return f"""

    Title

    {job.get('title','')}

    Experience

    {job.get('experience','')}

    Education

    {job.get('education','')}

    Skills

    {' '.join(job.get('skills',[]))}

    Responsibilities

    {' '.join(job.get('responsibilities',[]))}

    Qualifications

    {' '.join(job.get('qualifications',[]))}

    Nice To Have

    {' '.join(job.get('nice_to_have',[]))}

    """.strip()




        # =====================================================
    # Process Job
    # =====================================================

    def process_job(

        self,

        job,

        department: str,

        designation: str,

        top_k: int,

        raw_job_description: str,

    ):

        # --------------------------------------------
        # Build Job Embedding Text
        # --------------------------------------------

        job_text = self.build_job_embedding_text(

            job

        )

        # --------------------------------------------
        # Generate Job Embedding
        # --------------------------------------------

        job_embedding = self.embedding_service.generate_embedding(

            job_text

        )

        logger.info(

            "Job embedding generated."

        )

        # --------------------------------------------
        # Check Cache
        # --------------------------------------------

        cached_job = self.cache_service.find_similar_job(

            embedding=job_embedding,

            department=department,

            designation=designation,

        )

        if cached_job:

            logger.info(

                "Cache Hit."

            )

            return self.search_repository.get_search_results(

                str(

                    cached_job["_id"]

                )

            )

        logger.info(

            "Cache Miss."

        )

        # --------------------------------------------
        # Save Job
        # --------------------------------------------

        job_id = self.job_repository.create_job(

            job=job,

            embedding=job_embedding,

            department=department,

            designation=designation,

            search_period="ALL",

        )

        logger.info(

            f"Job Created : {job_id}"

        )

        # Continue to vector search

        return self.vector_search(

            job_id,

            job,

            job_text,

            job_embedding,

            top_k,

            raw_job_description,

        )
    


        # =====================================================
    # Vector Search
    # =====================================================

    def vector_search(

        self,

        job_id: str,

        job,

        job_text: str,

        job_embedding: list,

        top_k: int,

        raw_job_description: str,

    ):

        logger.info(

            "Running Atlas Vector Search..."

        )

        vector_results = self.embedding_repository.search_similar_embeddings(

            embedding=job_embedding,

            top_n=100,

        )

        logger.info(

            f"Retrieved {len(vector_results)} candidates."

        )

        candidates = []

        for result in vector_results:

            profile = self.profile_repository.get_profile(

                result["resume_id"]

            )

            if profile is None:

                continue

            profile["semantic_score"] = result.get(

                "embedding_score",

                0,

            )

            candidates.append(

                profile

            )

        logger.info(

            f"Loaded {len(candidates)} candidate profiles."

        )

        return self.rerank_candidates(

            job_id,

            job,

            job_text,

            candidates,

            top_k,

            raw_job_description,

        )
    

        # =====================================================
    # Rerank Candidates
    # =====================================================

    def rerank_candidates(

        self,

        job_id: str,

        job,

        job_text: str,

        candidates: list,

        top_k: int,

        raw_job_description: str,

    ):

        logger.info(

            "Running Cross Encoder Reranker..."

        )

        for candidate in candidates:

            candidate["resume_text"] = f"""

Candidate

{candidate.get('candidate_name','')}

Experience

{candidate.get('total_experience','')}

Skills

{' '.join(candidate.get('skills', []))}

Projects

{
chr(10).join(
    [
        p.get("description","")
        for p in candidate.get("projects",[])
    ]
)
}

"""

        candidates = self.reranker_service.rerank_candidates(

            job_text,

            candidates,

        )

        candidates = self.reranker_service.top_candidates(

            candidates,

            top_k,

        )

        logger.info(

            f"Top {len(candidates)} candidates selected."

        )

        return self.score_candidates(

            job_id,

            job,

            candidates,

            raw_job_description,

        )
    
        # =====================================================
    # Score Candidates
    # =====================================================

    def score_candidates(

        self,

        job_id: str,

        job,

        candidates: list,

        raw_job_description: str,

    ):

        logger.info(

            "Calculating ATS Scores..."

        )

        required_skills = [

            skill.lower()

            for skill in job.get(

                "skills",

                [],

            )

        ]

        scored_candidates = []

        for candidate in candidates:

            candidate_skills = [

                skill.lower()

                for skill in candidate.get(

                    "skills",

                    [],

                )

            ]

            matched_skills = [

                skill

                for skill in candidate_skills

                if skill in required_skills

            ]

            missing_skills = [

                skill

                for skill in required_skills

                if skill not in candidate_skills

            ]

            skill_match_percentage = 0

            if required_skills:

                skill_match_percentage = round(

                    (

                        len(matched_skills)

                        /

                        len(required_skills)

                    ) * 100,

                    2,

                )

            final_score = self.scoring_service.final_score(

                similarity_score=candidate.get(

                    "semantic_score",

                    0,

                ),

                matched_skills=matched_skills,

                required_skills=required_skills,

                candidate_years=0,

                required_years=0,

                education_match=True,

                certification_match=False,

            )

            candidate["matched_skills"] = matched_skills

            candidate["missing_skills"] = missing_skills

            candidate["skill_match_percentage"] = skill_match_percentage

            candidate["final_score"] = final_score

            scored_candidates.append(

                candidate

            )

        scored_candidates.sort(

            key=lambda x: x["final_score"],

            reverse=True,

        )

        return self.generate_reasoning(

            job_id,

            job,

            scored_candidates,

            raw_job_description,

        )
    


        # =====================================================
    # Generate Candidate Reasoning
    # =====================================================

    def generate_reasoning(

        self,

        job_id: str,

        job,

        candidates: list,

        raw_job_description: str,

    ):

        logger.info(

            "Generating AI Reasoning..."

        )

        for candidate in candidates:

            prompt = build_reasoning_prompt(

                job,

                candidate,

            )

            reasoning = self.openai_service.generate(

                prompt

            )

            candidate["reasoning"] = reasoning

        self.search_repository.save_search_results(

            job_id,

            candidates,

        )

        self.job_repository.update_result_count(

            job_id,

            len(candidates),

        )

        self.job_repository.update_status(

            job_id,

            "COMPLETED",

        )

        logger.info(

            "Search Completed."

        )

        return {

            "job_id": job_id,

            "total_candidates": len(

                candidates

            ),

            "results": candidates,

        }
    def get_candidate_reasoning(

    self,

    job_id: str,

    resume_id: str,

):

        reasoning = self.search_repository.get_reasoning(

            job_id,

            resume_id,

        )

        if reasoning and reasoning.get(

            "reasoning_generated"

        ):

            return reasoning

        candidate = self.search_repository.get_candidate(

            job_id,

            resume_id,

        )

        job = self.job_repository.get_job(

            job_id,

        )

        prompt = build_reasoning_prompt(

            job,

            candidate,

        )

        reasoning_text = self.openai_service.generate(

            prompt

        )

        self.search_repository.save_reasoning(

            job_id,

            resume_id,

            reasoning_text,

        )

        return {

            "resume_id": resume_id,

            "reasoning": reasoning_text,

        }