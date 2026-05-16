"""OpenRouter API client for the interview prep app."""

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def get_client():
    """Create and return an OpenRouter client."""
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ["OPENROUTER_API_KEY"],
    )


def load_prompt(filename):
    """Load a prompt from the prompts/ folder."""
    path = os.path.join("prompts", filename)
    with open(path, "r") as f:
        return f.read()


def chat(
    system_prompt, user_message, model="openrouter/free", temperature=0, max_tokens=2000
):
    """Send a message to OpenRouter and return the response."""
    client = get_client()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return {
        "content": response.choices[0].message.content,
        "tokens": response.usage.total_tokens,
        "model": response.model,
    }
