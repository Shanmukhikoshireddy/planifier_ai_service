import json

from app.config.logging import logger

from app.services.shared.openai_service import OpenAIService


class ResumeExtractorService:
    """
    Responsible for extracting structured resume data
    from raw resume text using Gemini.
    """

    def __init__(self):

        self.llm = OpenAIService()

    # Extract Resume

    def extract_resume(
        self,
        raw_text: str,
    ) -> dict:

        logger.info(
            "Extracting structured resume..."
        )

        prompt = self._build_prompt(
            raw_text
        )

        resume = self.llm.generate_json(
            [
                {
                    "role": "system",
                    "content": (
                        "You are an expert HR Resume Parser. "
                        "Return ONLY valid JSON."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ]
        )

        resume = self._validate_resume(
            resume
        )

        logger.info(
            "Resume extracted successfully."
        )

        return resume

    # Prompt

    def _build_prompt(
        self,
        raw_text: str,
    ) -> str:

        return f"""
Extract the following information from the resume.

Return ONLY JSON.

{{
    "candidate_name":"",
    "email":"",
    "phone":"",
    "location":"",
    "summary":"",
    "experience_years":0,
    "skills":[],
    "education":[],
    "projects":[],
    "certifications":[],
    "designation":"",
    "job_position":"",
    "current_company":""
}}

Resume

-----------------------

{raw_text}

-----------------------

Rules

1. Return ONLY JSON.
2. Never return markdown.
3. Missing values should be empty string.
4. Arrays should never be null.
5. experience_years must be numeric.
"""

    # Validate Resume

    def _validate_resume(
        self,
        resume: dict,
    ) -> dict:

        defaults = {

            "candidate_name": "",

            "email": "",

            "phone": "",

            "location": "",

            "summary": "",

            "experience_years": 0,

            "skills": [],

            "education": [],

            "projects": [],

            "certifications": [],

            "designation": "",

            "job_position": "",

            "current_company": "",

        }

        for key, value in defaults.items():

            if key not in resume:

                resume[key] = value

        return resume

    # Resume Text for Embedding

    def build_embedding_text(
        self,
        resume: dict,
    ) -> str:

        parts = [

            resume.get(
                "summary",
                "",
            ),

            " ".join(

                resume.get(
                    "skills",
                    [],
                )

            ),

            " ".join(

                resume.get(
                    "education",
                    [],
                )

            ),

            " ".join(

                resume.get(
                    "projects",
                    [],
                )

            ),

            " ".join(

                resume.get(
                    "certifications",
                    [],
                )

            ),

        ]

        return "\n".join(parts)