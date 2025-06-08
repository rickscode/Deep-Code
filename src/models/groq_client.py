import httpx
from typing import Any, Dict, List, Optional

GROQ_CONFIG = {
    "base_url": "https://api.groq.com/openai/v1",
    "rate_limits": {
        "requests_per_minute": 30,
        "tokens_per_minute": 6000
    }
}

class APIError(Exception):
    """API-related errors"""
    pass

class GroqClient:
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        self.api_key = api_key
        self.base_url = base_url or GROQ_CONFIG["base_url"]
        self.session = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"}
        )

    async def chat_completion(self, messages: List[Dict[str, Any]], model: str = "llama-3.3-70b-versatile") -> Dict[str, Any]:
        try:
            response = await self.session.post(
                "/chat/completions",
                json={"model": model, "messages": messages}
            )
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            raise APIError(f"API request failed: {e}")
        except httpx.HTTPStatusError as e:
            raise APIError(f"API returned error: {e.response.text}")
