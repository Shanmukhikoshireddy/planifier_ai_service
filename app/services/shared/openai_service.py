# import json
# import time

# from openai import OpenAI

# from app.config.settings import settings
# from app.config.logging import logger


# class OpenAIService:
#     """
#     Shared OpenAI Service

#     Used by:
#         • Resume Ingestion
#         • Job Parsing
#         • Candidate Reasoning
#         • Search Explanation
#     """

#     _client = None

#     def __init__(self):

#         if OpenAIService._client is None:

#             logger.info("Initializing OpenAI Client...")

#             OpenAIService._client = OpenAI(

#                 api_key=settings.OPENAI_API_KEY,

#             )

#             logger.info("OpenAI Client Initialized.")

#         self.client = OpenAIService._client

#         self.model = settings.OPENAI_MODEL

#     # =====================================================
#     # Generic Chat Completion
#     # =====================================================

#     def generate(

#         self,

#         prompt: str,

#         temperature: float = 0,

#         response_format: dict | None = None,

#     ):

#         start = time.time()

#         kwargs = {

#             "model": self.model,

#             "messages": [

#                 {

#                     "role": "user",

#                     "content": prompt,

#                 }

#             ],

#             "temperature": temperature,

#         }

#         if response_format:

#             kwargs["response_format"] = response_format

#         response = self.client.chat.completions.create(

#             **kwargs

#         )

#         logger.info(

#             f"OpenAI Response Time : {round(time.time()-start,2)} sec"

#         )

#         return response.choices[0].message.content

#     # =====================================================
#     # JSON Generation
#     # =====================================================

#     def generate_json(

#         self,

#         prompt: str,

#     ):

#         response = self.generate(

#             prompt=prompt,

#             temperature=0,

#             response_format={

#                 "type": "json_object"

#             }

#         )

#         return json.loads(

#             response

#         )

#     # =====================================================
#     # Health Check
#     # =====================================================

#     def health_check(

#         self,

#     ) -> bool:

#         try:

#             self.generate(

#                 "Reply only with OK."

#             )

#             return True

#         except Exception as e:

#             logger.exception(e)

#             return False







import json

from google import genai

from app.config.settings import settings
from app.config.logging import logger


class OpenAIService:
    """
    Wrapper around Gemini API.

    NOTE:
    Keep the class name as OpenAIService so that
    no other code changes are required.

    Later this file can be replaced with
    the real OpenAI implementation.
    """

    def __init__(self):

        logger.info(

            "Initializing Gemini..."

        )

        self.client = genai.Client(

            api_key=settings.GEMINI_API_KEY,

        )

        self.model = settings.GEMINI_MODEL

        logger.info(

            f"Gemini Model : {self.model}"

        )

    # =====================================================
    # Generate Text
    # =====================================================

    def generate(

        self,

        messages,

    ) -> str:

        try:

            prompt = self._build_prompt(

                messages

            )

            response = self.client.models.generate_content(

                model=self.model,

                contents=prompt,

            )

            return response.text.strip()

        except Exception as e:

            logger.exception(e)

            raise

    # =====================================================
    # Generate JSON
    # =====================================================

    def generate_json(

        self,

        messages,

    ) -> dict:

        response = self.generate(

            messages

        )
        response = response.strip()

        start = response.find("{")
        end = response.rfind("}")

        if start != -1 and end != -1:
            response = response[start:end+1]

        return json.loads(response)

        try:

            return json.loads(

                response

            )

        except json.JSONDecodeError:

            logger.error(

                "Gemini returned invalid JSON."

            )

            logger.error(

                response

            )

            raise ValueError(

                "Invalid JSON returned by Gemini."

            )

    # =====================================================
    # Health Check
    # =====================================================

    def health_check(

        self,

    ) -> bool:

        try:

            response = self.client.models.generate_content(

                model=self.model,

                contents="Reply with OK.",

            )

            return (

                response.text.strip().upper()

                == "OK"

            )

        except Exception:

            return False

    # =====================================================
    # Build Prompt
    # =====================================================

    def _build_prompt(

        self,

        messages,

    ) -> str:

        """
        Converts OpenAI-style messages into a single prompt
        for Gemini.
        """

        prompt = ""

        for message in messages:

            role = message["role"].upper()

            content = message["content"]

            prompt += f"{role}:\n{content}\n\n"

        return prompt.strip()