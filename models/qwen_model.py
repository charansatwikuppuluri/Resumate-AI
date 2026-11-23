
from openai import OpenAI

# Connect to LM Studio
client = OpenAI(
    base_url="http://127.0.0.1:1234/v1",
    api_key="lm-studio"
)

MODEL_NAME = "qwen2.5-coder-7b-instruct"


def ask_qwen(prompt):
    """Send a prompt to the local Qwen model."""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert AI resume analyst. Give clear, accurate and practical career advice."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=1500
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"AI connection error: {e}"
