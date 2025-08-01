import os
import openai
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_chat_completion(prompt: str, model: Optional[str] = "gpt-4", max_tokens: Optional[int] = 150) -> Optional[str]:
    """
    Generates a chat completion response from OpenAI's API.

    Parameters:
    - prompt (str): The input prompt for the model.
    - model (Optional[str]): The model to use for generating the response. Defaults to "gpt-4".
    - max_tokens (Optional[int]): The maximum number of tokens in the response. Defaults to 150.

    Returns:
    - Optional[str]: The generated response or None if an error occurs.
    """
    # Ensure the API key is retrieved securely
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")

    openai.api_key = api_key

    # Validate model
    allowed_models = ["gpt-3.5-turbo", "gpt-4"]
    if model not in allowed_models:
        raise ValueError(f"Model '{model}' is not allowed. Choose from {allowed_models}.")

    try:
        sanitized_prompt = sanitize_input(prompt)
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": sanitized_prompt}],
            max_tokens=max_tokens,
            stop=None  # Define stop sequences if necessary
        )
        return response.choices[0].message['content'].strip()
    except openai.error.OpenAIError as e:
        logger.error(f"An error occurred: {e}")
        return None

# Ensure input prompt is sanitized
def sanitize_input(prompt: str) -> str:
    """
    Sanitizes the input prompt to prevent potential security issues.

    Parameters:
    - prompt (str): The input prompt to sanitize.

    Returns:
    - str: The sanitized prompt.
    """
    # Implement sanitization logic as needed
    return prompt.strip()  # Example of basic sanitization
