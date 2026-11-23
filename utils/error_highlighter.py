
import json
import re

from models.qwen_model import ask_qwen


def analyze_resume_errors(resume_text):
    """
    Analyze resume text and identify mistakes using local Qwen AI.
    Only return issues whose quoted text actually exists in the resume.
    """

    if not isinstance(resume_text, str) or not resume_text.strip():
        return {
            "issues": [],
            "summary": "No resume text provided."
        }

    prompt = f"""
You are an expert resume reviewer.

Analyze the following resume and identify:

1. Grammar mistakes
2. Spelling mistakes
3. Weak or unclear sentences
4. Weak resume bullet points
5. Missing or weak action verbs
6. Unclear or unprofessional wording

IMPORTANT RULES:
- Only report genuine issues.
- Do not invent mistakes.
- Do not invent resume content.
- Quote the exact text from the resume.
- Keep suggestions professional and concise.
- Do not report something as missing if it is not necessary.

Return ONLY valid JSON in this exact format:

{{
    "summary": "Short summary of resume writing quality",
    "issues": [
        {{
            "exact_text": "Exact sentence or phrase from resume",
            "issue_type": "Grammar / Spelling / Weak wording / Action verb",
            "explanation": "Why this needs improvement",
            "suggestion": "Improved version of the text"
        }}
    ]
}}

If no genuine mistakes are found, return an empty issues list.

RESUME:
{resume_text[:10000]}
"""

    response = ask_qwen(prompt)

    if not response or response.startswith("AI connection error:"):
        return {
            "issues": [],
            "summary": response or "AI returned no response."
        }

    try:
        # Remove Markdown code fences if Qwen adds them
        cleaned_response = re.sub(
            r"^```(?:json)?\s*|\s*```$",
            "",
            response.strip(),
            flags=re.IGNORECASE
        )

        result = json.loads(cleaned_response)

        issues = result.get("issues", [])

        if not isinstance(issues, list):
            raise ValueError("Invalid issues format")

        # Verify that every quoted passage exists in the resume
        verified_issues = []

        for issue in issues:

            if not isinstance(issue, dict):
                continue

            exact_text = issue.get("exact_text", "")

            if (
                isinstance(exact_text, str)
                and exact_text.strip()
                and exact_text in resume_text
            ):
                verified_issues.append(issue)

        return {
            "summary": result.get(
                "summary",
                "Resume analysis completed."
            ),
            "issues": verified_issues
        }

    except (json.JSONDecodeError, ValueError, TypeError):
        return {
            "summary": "Could not read the AI response in the expected format. Please try again.",
            "issues": []
        }
