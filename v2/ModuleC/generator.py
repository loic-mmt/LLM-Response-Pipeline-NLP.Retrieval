from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from v2.ModuleB.policy_engine import ReactionPlan


@dataclass(frozen=True)
class GenerationConstraints:
    max_chars: int = 120
    forbid_mentions: bool = True
    forbid_hashtags: bool = True


def load_templates(path: str) -> list[str]:
    """Load response templates with slots."""
    # TODO: Parse a template file or JSON list of template strings.
    raise NotImplementedError("TODO: implement template loading")


def render_from_template(
    prompt: str,
    reaction_plan: ReactionPlan,
    template: str,
) -> str:
    """Render a response using a template and reaction plan."""
    # TODO: Map reaction plan fields to template slots.
    raise NotImplementedError("TODO: implement template rendering")


def apply_constraints(text: str, constraints: GenerationConstraints) -> str:
    """Enforce output constraints (length, banned patterns)."""
    # TODO: Strip mentions/hashtags and clamp length.
    raise NotImplementedError("TODO: implement constraint enforcement")


def generate_response(
    prompt: str,
    reaction_plan: ReactionPlan,
    templates: Sequence[str],
    constraints: GenerationConstraints | None = None,
) -> str:
    """Generate the final response text."""
    # TODO: Pick template, render, optionally call LLM, apply constraints.
    raise NotImplementedError("TODO: implement response generation")
