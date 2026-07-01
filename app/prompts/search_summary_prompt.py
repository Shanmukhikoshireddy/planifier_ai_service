SYSTEM_PROMPT = """
You are an AI Hiring Assistant.

Summarize the overall search results.

Mention

• Total candidates

• Overall skill coverage

• Experience distribution

• Best candidate

• Hiring recommendation

Limit to 200 words.
"""


USER_PROMPT = """
Search Results

{results}
"""


def build_search_summary_prompt(

    results,

):

    return [

        {

            "role": "system",

            "content": SYSTEM_PROMPT,

        },

        {

            "role": "user",

            "content": USER_PROMPT.format(

                results=results,

            ),

        },

    ]