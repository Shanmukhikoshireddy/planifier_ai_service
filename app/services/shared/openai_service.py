


import json

from google import genai
import time

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

          
            for attempt in range(3):

                try:

                    response = self.client.models.generate_content(

                        model=self.model,

                        contents=prompt,

                    )

                    return response.text.strip()

                except Exception as e:

                    logger.warning(

                        f"Gemini attempt {attempt+1} failed."

                    )

                    if attempt == 2:

                        raise

                    time.sleep(5)

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

        response = self.generate(messages)

        response = response.strip()

        # Remove markdown if Gemini returns ```json
        if response.startswith("```"):
            response = response.replace("```json", "")
            response = response.replace("```", "")
            response = response.strip()

        start = response.find("{")
        end = response.rfind("}")

        if start != -1 and end != -1:
            response = response[start:end + 1]

        try:

            return json.loads(response)

        except json.JSONDecodeError:

            logger.error("Gemini returned invalid JSON.")

            logger.error(response)

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
            print("Gemini Response:",response.text)
            return (
                response.text.strip().upper()
                == "OK"
            )
        except Exception as e:
            print("Gemini health Error:",e)
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