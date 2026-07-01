SYSTEM_PROMPT = """
You are an AI Recruitment Assistant.

Convert Job Descriptions into structured JSON.

Rules

1. Return ONLY JSON.
2. Never explain.
3. Never invent skills.
4. Preserve recruiter intent.
5. Group similar skills.
6.Do not use markdown.
7.Do not wrap the JSON inside ```json.
"""


USER_PROMPT = """
Extract the following Job Description.

Schema

{{
    "title":"",
    "department":"",
    "experience":"",
    "education":"",
    "skills":[],
    "responsibilities":[],
    "qualifications":[],
    "nice_to_have":[]
}}

Job Description

{job_description}

"""


def build_job_prompt(

    job_description: str,

):

    return [

        {

            "role": "system",

            "content": SYSTEM_PROMPT,

        },

        {

            "role": "user",

            "content": USER_PROMPT.format(

                job_description=job_description,

            ),

        },

    ]