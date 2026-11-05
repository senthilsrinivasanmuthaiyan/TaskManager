import httpx
from .config import get_settings


class ModelGatewayError(RuntimeError):
    pass


async def chat(system: str, user: str, temperature: float = 0.2) -> str:
    settings = get_settings()
    url = settings.llm_base_url.rstrip("/") + "/chat/completions"
    headers = {"Authorization": f"Bearer {settings.llm_api_key}", "Content-Type": "application/json"}
    payload = {
        "model": settings.llm_model,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "temperature": temperature,
        "stream": False,
    }
    async with httpx.AsyncClient(timeout=180) as client:
        try:
            response = await client.post(url, headers=headers, json=payload)
        except httpx.HTTPError as exc:
            raise ModelGatewayError(
                f"Model endpoint unavailable at {settings.llm_base_url}. Start Ollama or configure a compatible endpoint."
            ) from exc
        if response.is_error:
            raise ModelGatewayError(f"Model API returned HTTP {response.status_code}: {response.text[:500]}")
        data = response.json()
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise ModelGatewayError("Model endpoint returned an unexpected Chat Completions response.") from exc
