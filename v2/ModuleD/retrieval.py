from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence


@dataclass(frozen=True)
class MemeTemplate:
    meme_id: str
    tags: list[str]
    constraints: dict


@dataclass(frozen=True)
class MemeCandidate:
    template: MemeTemplate
    score: float


def load_meme_catalog(path: str) -> list[MemeTemplate]:
    """Load meme templates with tags and text constraints."""
    # TODO: Parse metadata.jsonl and convert to MemeTemplate entries.
    raise NotImplementedError("TODO: implement catalog loading")


def score_template(
    template: MemeTemplate,
    prompt_tags: Sequence[str],
    response_tags: Sequence[str],
) -> float:
    """Score a single template against prompt and response tags."""
    # TODO: Implement weighted overlap or embedding similarity.
    raise NotImplementedError("TODO: implement template scoring")


def rank_templates(
    templates: Iterable[MemeTemplate],
    prompt_tags: Sequence[str],
    response_tags: Sequence[str],
    top_k: int = 5,
) -> list[MemeCandidate]:
    """Rank templates and return the top candidates."""
    # TODO: Compute scores for each template and return top_k.
    raise NotImplementedError("TODO: implement ranking")


def select_template(candidates: Sequence[MemeCandidate]) -> MemeTemplate:
    """Select the best meme template from ranked candidates."""
    # TODO: Pick top candidate or apply tie-break rules.
    raise NotImplementedError("TODO: implement selection")
