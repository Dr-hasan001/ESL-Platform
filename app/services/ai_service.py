"""
ai_service.py — Generate multiple-choice questions using Claude.
"""

import json
import re

from app.config import settings


def generate_questions(content: str, content_type: str, count: int) -> list[dict]:
    """
    Call Claude to generate `count` multiple-choice questions from `content`.
    Returns a list of dicts: [{question_text, options: [A,B,C,D], correct_index}]
    Raises ValueError if the API key is not configured or the response is malformed.
    """
    if not settings.anthropic_api_key:
        raise ValueError("ANTHROPIC_API_KEY is not configured.")

    import anthropic  # imported lazily so the package is only required when used

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    prompt = f"""You are an expert ESL teacher. Your task is to create comprehension questions.

Content type: {content_type}
Content:
\"\"\"
{content}
\"\"\"

Generate exactly {count} multiple-choice questions based on the content above.

Rules:
- Each question must be answerable from the content (no outside knowledge required)
- Each question must have exactly 4 options
- Only one option is correct
- Vary which option (A/B/C/D) is correct across questions

Return ONLY a valid JSON array — no preamble, no explanation, no markdown fences:
[
  {{
    "question_text": "...",
    "options": ["Option A text", "Option B text", "Option C text", "Option D text"],
    "correct_index": 0
  }}
]

correct_index is 0 for A, 1 for B, 2 for C, 3 for D."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()

    # Extract the JSON array even if the model wraps it in markdown fences
    match = re.search(r"\[[\s\S]*\]", raw)
    if not match:
        raise ValueError("AI response did not contain a JSON array.")

    questions = json.loads(match.group())

    # Basic validation
    for q in questions:
        if "question_text" not in q or "options" not in q or "correct_index" not in q:
            raise ValueError("AI response has unexpected question structure.")
        if len(q["options"]) != 4:
            raise ValueError("Each question must have exactly 4 options.")

    return questions
