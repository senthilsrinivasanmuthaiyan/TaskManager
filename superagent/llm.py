import httpx
from .config import get_settings


class DeepSeekError(RuntimeError):
    pass


async def chat(system: str, user: str, temperature: float = 0.2) -> str:
    settings = get_settings()
    if not settings.deepseek_api_key:
        raise DeepSeekError("DEEPSEEK_API_KEY is not configured. Add it to the local .env file.")
    url = settings.deepseek_base_url.rstrip("/") + "/chat/completions"
    headers = {"Authorization": f"Bearer {settings.deepseek_api_key}", "Content-Type": "application/json"}
    payload = {
        "model": settings.deepseek_model,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "temperature": temperature,
        "stream": False,
    }
    async with httpx.AsyncClient(timeout=90) as client:
        response = await client.post(url, headers=headers, json=payload)
        if response.is_error:
            raise DeepSeekError(f"DeepSeek API returned HTTP {response.status_code}: {response.text[:500]}")
        data = response.json()
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise DeepSeekError("DeepSeek returned an unexpected Chat Completions response.") from exc
