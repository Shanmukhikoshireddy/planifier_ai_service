SYSTEM_PROMPT = """
You are an experienced Technical Recruiter.

Summarize candidate search results for recruiters.

Return ONLY valid JSON.
"""


USER_PROMPT = """
Generate a recruiter-friendly summary.

Return ONLY valid JSON.

{{
    "summary": "",
    "top_strengths": [],
    "common_skill_gaps": [],
    "hiring_observations": [],
    "recommendation": ""
}}

Search Results

{{search_results}}
"""


def build_search_summary_prompt(
    search_results: str,
):

    return [

        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },

        {
            "role": "user",
            "content": USER_PROMPT.format(
                search_results=search_results,
            ),
        },

    ]