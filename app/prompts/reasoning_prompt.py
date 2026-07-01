SYSTEM_PROMPT = """
You are a Senior Technical Recruiter.

Your task is to explain candidate suitability.

Keep the explanation concise.

Do NOT repeat the resume.

Mention

• Matching skills

• Missing skills

• Experience relevance

• Strengths

• Weaknesses

• Final recommendation

Maximum 150 words.
"""


USER_PROMPT = """
Job

{job}

Candidate

{candidate}
"""


def build_reasoning_prompt(

    job,

    candidate,

):

    return [

        {

            "role": "system",

            "content": SYSTEM_PROMPT,

        },

        {

            "role": "user",

            "content": USER_PROMPT.format(

                job=job,

                candidate=candidate,

            ),

        },

    ]