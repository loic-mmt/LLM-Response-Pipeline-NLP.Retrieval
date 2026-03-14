from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence
import hashlib
import json
import re

from v2.ModuleB.policy_engine import ReactionPlan, normalize_token


@dataclass(frozen=True)
class GenerationConstraints:
    max_chars: int = 120
    forbid_mentions: bool = True
    forbid_hashtags: bool = True


@dataclass
class OllamaClient:
    model: str = "qwen2.5:3b-instruct"
    host: str = "http://127.0.0.1:11434"

    def complete(self, prompt: str, temperature: float = 0.2, max_tokens: int = 180) -> str:
        try:
            import requests
        except ImportError as exc:
            raise RuntimeError("requests is required to use OllamaClient") from exc

        r = requests.post(
            f"{self.host}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": temperature, "num_predict": max_tokens},
            },
            timeout=60,
        )
        r.raise_for_status()
        return r.json()["response"]


def load_templates(path: str) -> list[str]:
    """Load response templates with slots."""
    templates_path = Path(path)
    raw = templates_path.read_text(encoding="utf-8")

    # Accept JSON list or newline-delimited text.
    try:
        data = json.loads(raw)
        if not isinstance(data, list):
            raise ValueError("templates file must contain a JSON array")
        candidates = [str(item) for item in data]
    except json.JSONDecodeError:
        candidates = [line.strip() for line in raw.splitlines()]

    # Keep placeholders intact; normalize only whitespace.
    templates = [" ".join(str(t).split()) for t in candidates if str(t).strip()]
    if not templates:
        raise ValueError("no templates found")

    # Validate required slots at least once to ensure compatibility.
    required_slots = ("{tone}", "{acts}", "{intensity}", "{format}")
    for slot in required_slots:
        if not any(slot in template for template in templates):
            raise ValueError(f"at least one template must contain {slot}")

    return templates


def render_from_template(
    prompt: str,
    reaction_plan: ReactionPlan,
    template: str,
) -> str:
    """Render a response using a template and reaction plan."""
    if not reaction_plan.acts:
        acts_text = "acknowledge"
    elif len(reaction_plan.acts) == 1:
        acts_text = reaction_plan.acts[0]
    else:
        acts_text = " + ".join(reaction_plan.acts)

    slots = {
        "prompt": normalize_token(prompt),
        "tone": normalize_token(reaction_plan.tone),
        "acts": normalize_token(acts_text),
        "intensity": normalize_token(reaction_plan.intensity),
        "format": normalize_token(reaction_plan.format),
    }

    try:
        return template.format_map(slots)
    except KeyError as exc:
        raise ValueError(f"template is missing slot: {exc}") from exc


def remove_emojis(text: str) -> str:
    """Remove most emoji and pictographic unicode characters."""
    emoj = re.compile(
        "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002500-\U00002BEF"  # chinese char
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642"
        u"\u2600-\u2B55"
        u"\u200d"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\ufe0f"  # dingbats
        u"\u3030"
        "]+",
        re.UNICODE,
    )
    return re.sub(emoj, "", text)


def apply_constraints(text: str, constraints: GenerationConstraints) -> str:
    """Enforce output constraints (length, banned patterns)."""
    if constraints.forbid_mentions:
        text = re.sub(r"@\w+", "", text)
    if constraints.forbid_hashtags:
        text = re.sub(r"#\w+", "", text)

    text = remove_emojis(text)
    text = " ".join(text.split()).strip()

    if len(text) > constraints.max_chars:
        cut = text[: constraints.max_chars].rstrip()
        last_space = cut.rfind(" ")
        return cut if last_space == -1 else cut[:last_space]
    return text


def caption_with_llm(
    client: OllamaClient,
    user_prompt: str,
    draft_text: str,
    reaction_plan: ReactionPlan,
    max_chars: int,
) -> str:
    acts = ", ".join(reaction_plan.acts) if reaction_plan.acts else "acknowledge"
    prompt = f"""
Return ONLY JSON: {{"caption":"..."}}.

Rules:
- English unless the user prompt is clearly French.
- Max {max_chars} characters.
- No emojis.
- User said: {user_prompt}
- Rewrite the DRAFT_CAPTION.
- Match the vibe: tone={reaction_plan.tone}, acts={acts}, intensity={reaction_plan.intensity}, format={reaction_plan.format}
- Don't integrate the tags inside the caption.
- Make it meme-like: short, punchy.

DRAFT_CAPTION: {draft_text}
"""

    try:
        raw = client.complete(prompt, temperature=0.1, max_tokens=160).strip()
        s = raw[raw.find("{") : raw.rfind("}") + 1]
        obj = json.loads(s)
        cap = (obj.get("caption") or "").strip()
        if not cap:
            return draft_text
        return cap[:max_chars]
    except Exception:
        return draft_text


def generate_response(
    prompt: str,
    reaction_plan: ReactionPlan,
    templates: Sequence[str],
    constraints: GenerationConstraints | None = None,
    llm: bool = True,
) -> str:
    """Generate the final response text."""
    if not prompt or not prompt.strip():
        raise ValueError("prompt cannot be empty")
    if reaction_plan is None:
        raise ValueError("reaction_plan cannot be None")

    usable_templates = [str(t).strip() for t in templates if str(t).strip()]
    if not usable_templates:
        raise ValueError("templates cannot be empty")

    if constraints is None:
        constraints = GenerationConstraints()

    # Deterministic template selection for reproducible outputs.
    seed_text = "|".join(
        [
            normalize_token(prompt),
            normalize_token(reaction_plan.tone),
            normalize_token(" ".join(reaction_plan.acts)),
            normalize_token(reaction_plan.intensity),
            normalize_token(reaction_plan.format),
        ]
    )
    start_idx = int(hashlib.sha256(seed_text.encode("utf-8")).hexdigest(), 16) % len(usable_templates)

    draft_text = ""
    for offset in range(len(usable_templates)):
        idx = (start_idx + offset) % len(usable_templates)
        template = usable_templates[idx]
        try:
            draft_text = render_from_template(prompt=prompt, reaction_plan=reaction_plan, template=template)
        except ValueError:
            continue
        if draft_text.strip():
            break
    else:
        raise ValueError("no renderable template found")

    candidate_text = draft_text
    if llm:
        client = OllamaClient(model="qwen2.5:3b-instruct")
        candidate_text = caption_with_llm(
            client=client,
            user_prompt=prompt,
            draft_text=draft_text,
            reaction_plan=reaction_plan,
            max_chars=constraints.max_chars,
        )

    cleaned_text = apply_constraints(candidate_text, constraints)
    if not cleaned_text:
        cleaned_text = apply_constraints(draft_text, constraints)
    if not cleaned_text:
        cleaned_text = "..."

    return cleaned_text
