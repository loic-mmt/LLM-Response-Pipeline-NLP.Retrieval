from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence


@dataclass(frozen=True)
class ReactionPlan:
    tone: str
    acts: list[str]
    intensity: str
    format: str


def load_policy_rules(path: str) -> list[dict]:
    """Load rule definitions that map prompt tags to reaction tags."""
    # TODO: Define a small JSON/YAML rule format and parse it here.
    raise NotImplementedError("TODO: implement rule loading")


def score_rules(prompt_tags: Sequence[str], rules: Iterable[dict]) -> list[tuple[dict, float]]:
    """Score rules for a given set of prompt tags."""
    # TODO: Implement weighted matching and return sorted rule scores.
    raise NotImplementedError("TODO: implement rule scoring")


def derive_reaction_plan(prompt_tags: Sequence[str], rules: Iterable[dict]) -> ReactionPlan:
    """Derive reaction tags (tone/acts/intensity/format) from prompt tags."""
    # TODO: Select best rule or blend multiple rules into a single plan.
    raise NotImplementedError("TODO: implement reaction plan selection")


def reaction_plan_to_tags(plan: ReactionPlan) -> list[str]:
    """Flatten a reaction plan into response tags."""
    # TODO: Decide tag serialization format (e.g., tone:sarcastic).
    raise NotImplementedError("TODO: implement tag flattening")
