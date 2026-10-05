import os
import requests

MODEL = "nvidia/nemotron-3.5-lightning"

PROMPTS = {
    0: "You are a Socratic tutor. Ask a single short open guiding question (max 25 words). STRICT RULE: Do not state or reveal the answer.",
    1: "You are a Socratic tutor. Ask a single short question pointing where to look in the concept (max 25 words). STRICT RULE: Do not state or reveal the answer.",
    2: "You are a Socratic tutor. Give a gentle nudge with a brief partial clue (max 30 words). STRICT RULE: Do not state the final answer.",
    3: "You are a tutor providing resolution. Provide a clear 1-2 sentence explanation. Explicitly start with: Here is what you were working toward:"
}

FALLBACKS = {
    0: "What are the fundamental concepts or components that come to mind when thinking about this?",
    1: "Focus on the specific mechanism or definition in this area. Where should you look closer?",
    2: None,
    3: None
}

SKIP_PHRASES = ["just tell me", "give me the answer", "skip", "what is the answer", "tell me the answer", "i give up"]

def generate_response(question, chunk, level, last_attempt=None):
    if last_attempt:
        low = last_attempt.lower()
        for p in SKIP_PHRASES:
            if p in low and level > 0:
                level = 0
                break

    level = max(0, min(3, level))
    system_text = PROMPTS[level]

    user_content = f"Context: {chunk}\nQuestion: {question}"
    if last_attempt:
        user_content += f"\nStudent's previous attempt: {last_attempt}"

    api_key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("ANTHROPIC_API_KEY") or ""
    if api_key:
        base_url = os.environ.get("ANTHROPIC_BASE_URL") or "https://openrouter.ai/api/v1"
        url = f"{base_url.rstrip('/')}/chat/completions"
        try:
            r = requests.post(
                url,
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": os.environ.get("NEMOTRON_MODEL") or MODEL,
                    "messages": [
                        {"role": "system", "content": system_text},
                        {"role": "user", "content": user_content}
                    ],
                    "reasoning": {"effort": "none"},
                    "max_tokens": 150,
                    "temperature": 0.4
                },
                timeout=8
            )
            if r.status_code == 200:
                cnt = r.json()["choices"][0]["message"].get("content")
                if cnt and cnt.strip():
                    return cnt.strip()
        except Exception:
            pass

    if level == 2:
        words = chunk.split()
        snippet = " ".join(words[:25])
        return f"Consider this clue: '{snippet}...'. How does this connect to your question?"
    if level == 3:
        return f"Here is what you were working toward: {chunk}"

    return FALLBACKS.get(level, FALLBACKS[0])
