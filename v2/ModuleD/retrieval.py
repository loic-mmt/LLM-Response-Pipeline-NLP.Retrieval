from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import json
from pathlib import Path

from v2.ModuleB.policy_engine import normalize_token


@dataclass(frozen=True)
class MemeTemplate:
    meme_id: str
    tags: list[str]
    constraints: dict


@dataclass(frozen=True)
class MemeCandidate:
    template: MemeTemplate
    score: float


def load_jsonl(path: Path) -> list[dict]:
    items: list[dict] = []
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSON at line {line_no}: {exc.msg}") from exc
            if not isinstance(obj, dict):
                raise ValueError(f"line {line_no}: expected a JSON object")
            items.append(obj)
    return items


def profile_text(m: dict) -> str:
    # Encodage des tags et triggers
    tags = m.get("tags", [])
    triggers = m.get("triggers", [])
    return " | ".join(tags + triggers)


def load_meme_catalog(path: str) -> list[MemeTemplate]:
    """Load meme templates with tags and text constraints."""
    catalog_path = Path(path)
    memes = load_jsonl(catalog_path)
    templates: list[MemeTemplate] = []

    for line_no, meme in enumerate(memes, start=1):
        meme_id = meme.get("id")
        if not isinstance(meme_id, str) or not meme_id.strip():
            raise ValueError(f"line {line_no}: missing or invalid 'id'")

        raw_tags = meme.get("tags", [])
        if raw_tags is None:
            raw_tags = []
        if not isinstance(raw_tags, list):
            raise ValueError(f"line {line_no}: 'tags' must be a list")

        normalized_tags: list[str] = []
        seen: set[str] = set()
        for raw_tag in raw_tags:
            if not isinstance(raw_tag, str):
                raise ValueError(f"line {line_no}: all 'tags' values must be strings")
            tag = normalize_token(raw_tag)
            if not tag or tag in seen:
                continue
            seen.add(tag)
            normalized_tags.append(tag)

        text_cfg = meme.get("text", {})
        if text_cfg is None:
            text_cfg = {}
        if not isinstance(text_cfg, dict):
            raise ValueError(f"line {line_no}: 'text' must be an object when provided")

        file_name = meme.get("file")
        if file_name is not None and not isinstance(file_name, str):
            raise ValueError(f"line {line_no}: 'file' must be a string when provided")

        constraints = {
            "file": file_name,
            "text": text_cfg,
        }

        templates.append(
            MemeTemplate(
                meme_id=meme_id.strip(),
                tags=normalized_tags,
                constraints=constraints,
            )
        )

    if not templates:
        raise ValueError(f"no meme templates found in {catalog_path}")
    return templates




def _normalize_tag_list(values: Sequence[str] | None) -> list[str]:
    """Normalize and deduplicate tag lists while preserving order."""
    if values is None:
        return []

    normalized: list[str] = []
    seen: set[str] = set()
    for value in values:
        if not isinstance(value, str):
            continue
        raw_value = value.strip()

        # Keep both the full token and the suffix if a prefix exists.
        candidates = [raw_value]
        if ":" in raw_value:
            _, suffix = raw_value.split(":", 1)
            candidates.append(suffix)

        for candidate in candidates:
            token = normalize_token(candidate)
            if not token or token in seen:
                continue
            seen.add(token)
            normalized.append(token)
    return normalized


def score_template(
    template: MemeTemplate,
    prompt_tags: Sequence[str],
    response_tags: Sequence[str],
) -> float:
    """Score a single template against prompt and response tags."""
    if template is None:
        raise ValueError("template cannot be None")

    template_norm = _normalize_tag_list(template.tags)
    prompt_norm = _normalize_tag_list(prompt_tags)
    response_norm = _normalize_tag_list(response_tags)

    template_set = set(template_norm)
    prompt_set = set(prompt_norm)
    response_set = set(response_norm)

    prompt_overlap = len(template_set.intersection(prompt_set)) / max(1, len(prompt_set))
    response_overlap = len(template_set.intersection(response_set)) / max(1, len(response_set))

    # Response tags are more important than prompt tags for final meme selection.
    score = (0.4 * prompt_overlap) + (0.6 * response_overlap)

    if score < 0.0:
        return 0.0
    if score > 1.0:
        return 1.0
    return float(score)


def rank_templates(
    templates: Iterable[MemeTemplate],
    prompt_tags: Sequence[str],
    response_tags: Sequence[str],
    top_k: int = 5,
) -> list[MemeCandidate]:
    """Rank templates and return the top candidates."""
    if top_k <= 0:
        raise ValueError("top_k must be > 0")

    template_list = list(templates)
    candidates: list[MemeCandidate] = []
    for template in template_list:
        score = score_template(template, prompt_tags, response_tags)
        candidates.append(MemeCandidate(template=template, score=score))

    # Deterministic ordering: highest score first, then meme_id ascending.
    candidates.sort(key=lambda c: (-c.score, c.template.meme_id))
    return candidates[:top_k]


def select_template(candidates: Sequence[MemeCandidate]) -> MemeTemplate:
    """Select the best meme template from ranked candidates."""
    if candidates is None:
        raise ValueError("candidates cannot be None")

    candidate_list = list(candidates)
    if not candidate_list:
        raise ValueError("candidates cannot be empty")

    # Defensive sort in case callers pass an unsorted list.
    candidate_list.sort(key=lambda c: (-c.score, c.template.meme_id))
    return candidate_list[0].template
