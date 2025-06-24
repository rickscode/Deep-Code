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
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=120.0  # 2 minute timeout
        )
        self.rate_limited_models = set()  # Track models that are rate limited

    async def chat_completion_with_fallback(self, messages: List[Dict[str, Any]], default_model: str, fallback_models: List[str] = None) -> Dict[str, Any]:
        """Try default model first, then fallback models if rate limited"""
        models_to_try = [default_model] + (fallback_models or [])
        
        for model in models_to_try:
            if model in self.rate_limited_models:
# Skip silently
                continue
                
            try:
                return await self.chat_completion(messages, model)
            except APIError as e:
                if "rate limit" in str(e).lower():
# Rate limit hit, try next model silently
                    self.rate_limited_models.add(model)
                    continue
                else:
                    # For non-rate-limit errors, don't try other models
                    raise e
        
        # If all models are rate limited
        raise APIError("All available models are rate limited. Please wait a few minutes and try again.")

    async def chat_completion(self, messages: List[Dict[str, Any]], model: str = "llama-3.3-70b-versatile") -> Dict[str, Any]:
        import asyncio
        
        for attempt in range(3):  # Try up to 3 times
            try:
                response = await self.session.post(
                    "/chat/completions",
                    json={"model": model, "messages": messages}
                )
                response.raise_for_status()
                return response.json()
            except httpx.ReadTimeout:
                if attempt < 2:  # Don't wait after the last attempt
                    print(f"[Timeout] Retrying in {2 ** attempt} seconds... (attempt {attempt + 1}/3)")
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    raise APIError("API request timed out after 3 attempts. Try a simpler request or check your internet connection.")
            except httpx.RequestError as e:
                if attempt < 2 and "timeout" in str(e).lower():
                    print(f"[Network Error] Retrying in {2 ** attempt} seconds... (attempt {attempt + 1}/3)")
                    await asyncio.sleep(2 ** attempt)
                    continue
                else:
                    import traceback
                    tb = traceback.format_exc()
                    raise APIError(f"API request failed: {e.__class__.__name__}: {e}\nTraceback:\n{tb}")
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:  # Rate limit
                    raise APIError(f"Rate limit exceeded: {e.response.text}")
                else:
                    # Don't retry other HTTP status errors (like 401, 413, etc.)
                    raise APIError(f"API returned error: {e.response.status_code} {e.response.text}")
