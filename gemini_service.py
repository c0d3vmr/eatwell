"""Shared Gemini API client helpers."""

import os


class GeminiRequestError(RuntimeError):
    """A safe, user-facing Gemini API failure."""


def generate_text(prompt: str, api_key: str | None = None) -> str:
    """Generate text with the current Google Gen AI SDK."""
    key = (api_key or os.getenv("GEMINI_API_KEY", "")).strip()
    if not key:
        raise GeminiRequestError(
            "GEMINI_API_KEY is missing. Add it to .env and restart Streamlit."
        )

    try:
        from google import genai
    except ImportError as exc:
        raise GeminiRequestError(
            "The Google Gen AI SDK is not installed. Run "
            "`python -m pip install -r requirements.txt` in the app environment."
        ) from exc

    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
    if not model:
        model = "gemini-2.5-flash"
    try:
        client = genai.Client(api_key=key)
        response = client.models.generate_content(
            model=model,
            contents=prompt,
        )
    except Exception as exc:
        message = str(exc).lower()
        provider_error = str(exc).replace(key, "[redacted]").strip()
        if len(provider_error) > 500:
            provider_error = provider_error[:497] + "..."
        if any(term in message for term in ("api key", "api_key", "unauthorized", "401", "403")):
            detail = (
                "Gemini rejected the API key. Check that GEMINI_API_KEY is the "
                "Google AI Studio key, with no extra quotes/spaces, and restart Streamlit."
            )
        elif any(term in message for term in ("quota", "resource_exhausted", "429")):
            detail = (
                "Gemini's quota or rate limit was reached. Check the project's "
                "Gemini API quota and try again later."
            )
        elif "404" in message or "not found" in message:
            detail = (
                f"Gemini returned a 404 for model '{model}'. Provider details: "
                f"{provider_error}"
            )
        elif any(term in message for term in ("timeout", "connect", "network", "dns")):
            detail = "Could not connect to Gemini. Check the network and try again."
        else:
            detail = f"Gemini request failed ({type(exc).__name__}): {provider_error}"
        raise GeminiRequestError(detail) from exc

    try:
        text = response.text
    except (AttributeError, ValueError):
        text = None
    if not isinstance(text, str) or not text.strip():
        raise GeminiRequestError(
            "Gemini returned no text. The request may have been blocked or filtered."
        )
    return text.strip()
