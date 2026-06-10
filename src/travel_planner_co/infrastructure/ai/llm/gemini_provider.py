from collections.abc import AsyncGenerator

from src.travel_planner_co.infrastructure.constants import TRAVEL_PLANNER_CO_SYSTEM_PROMPT
from travel_planner_co.infrastructure.ai.llm.base import LLMProvider
from google import genai
from google.genai import types


class GeminiProvider(LLMProvider):
    
    def __init__(self, api_key: str, model: str):
        self.client = genai.Client(api_key=api_key)
        self.model = model


    async def generate(self, prompt: str, system_instruction: str = TRAVEL_PLANNER_CO_SYSTEM_PROMPT, temperature: float = 0.5) -> str:

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=temperature,
                system_instruction=system_instruction
            )
        )
        return response.text
    
    async def stream_generate(
        self,
        prompt: str,
        system_instruction: str = TRAVEL_PLANNER_CO_SYSTEM_PROMPT,
        temperature: float = 0.5,
    ) -> AsyncGenerator[str, None]:

        for chunk in self.client.models.generate_content_stream(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=temperature,
                system_instruction=system_instruction
            )
        ):
        
            if chunk.text:
                yield chunk.text

        