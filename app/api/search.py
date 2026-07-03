from fastapi import APIRouter
from fastapi import HTTPException

from app.dto.request.search_request import SearchRequest

from app.services.search.search_service import SearchService
import traceback
from app.config.logging import logger
from app.repository.search_repository import SearchRepository
from app.repository.job_repository import JobRepository


router = APIRouter(

    prefix="/cv-service/search",

    tags=["Candidate Search"],

)

search_service = SearchService()

search_repository = SearchRepository()

job_repository = JobRepository()

# =====================================================
# Search History
# =====================================================

@router.get(

    "/history",

)

def search_history():

    return job_repository.get_all_jobs()

# Search Candidates


@router.post("")

def search_candidates(

    request: SearchRequest,

):

    try:

        return search_service.search(
            department=request.department,
            job_description=request.job_description,
            search_period=request.search_period,
            page=request.page,
            page_size=request.page_size,
        )

    except Exception as e: 
        raise HTTPException(
            status_code=500,
            detail=str(e),

        )


# =====================================================
# Get Search Results
# =====================================================

@router.get(

    "/{job_id}",

)

def get_search_results(
    job_id: str,
):
    results = search_repository.get_search_results(
        job_id
    )
    if len(results) == 0:
        raise HTTPException(
            status_code=404,
            detail="Search Results Not Found.",
        )

    return {

        "job_id": job_id,

        "total_candidates": len(results),

        "results": results,

    }


# =====================================================
# Candidate Reasoning
# =====================================================

@router.get(

    "/reasoning/{job_id}/{resume_id}",

)

def get_reasoning(

    job_id: str,

    resume_id: str,

):

    try:

        return search_service.get_candidate_reasoning(

            job_id,

            resume_id,

        )

    
    except Exception as e:

        logger.exception(e)

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


