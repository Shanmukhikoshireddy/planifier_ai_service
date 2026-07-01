SYSTEM_PROMPT = """
You are an expert Resume Parsing AI.

Your task is to convert resumes into structured JSON.

Rules:

1. Return ONLY valid JSON.
2. Never explain anything.
3. Never generate markdown.
4. Missing fields should be empty strings or empty arrays.
5. Preserve information exactly as written.
6. Do not invent data.
7. Normalize skills into simple readable names.
8. Extract every project, education, experience and certification.
9. Dates should remain exactly as written.
"""


USER_PROMPT = """
Extract the following Resume into JSON.

Required Schema

{{
    "candidate_name":"",
    "email":"",
    "phone":"",
    "location":"",
    "linkedin":"",
    "github":"",
    "portfolio":"",
    "total_experience":"",
    "skills":[],
    "education":[
        {{
            "degree":"",
            "specialization":"",
            "institution":"",
            "year":""
        }}
    ],
    "experience":[
        {{
            "company":"",
            "designation":"",
            "duration":"",
            "description":""
        }}
    ],
    "projects":[
        {{
            "title":"",
            "description":"",
            "technologies":[]
        }}
    ],
    "certifications":[
        {{
            "name":"",
            "issuer":"",
            "year":""
        }}
    ]
}}

Resume

{resume}
"""


def build_resume_prompt(

    resume: str,

):

    return [

        {

            "role": "system",

            "content": SYSTEM_PROMPT,

        },

        {

            "role": "user",

            "content": USER_PROMPT.format(

                resume=resume,

            ),

        },

    ]