from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence


@dataclass(frozen=True)
class TagPrediction:
    tag: str
    score: float


def load_tag_dictionary(path: str) -> list[str]:
    """Load the allowed tag dictionary from disk."""
    # TODO: Parse tags.jsonl or a similar source and return a stable tag list.
    raise NotImplementedError("TODO: implement tag dictionary loading")


def normalize_prompt(prompt: str) -> str:
    """Normalize prompt text before vectorization or inference."""
    # TODO: Add consistent normalization (lowercasing, punctuation cleanup).
    return prompt.strip()


def train_multilabel_classifier(
    texts: Sequence[str],
    labels: Sequence[Sequence[str]],
    tag_dictionary: Sequence[str],
):
    """Train a multi-label classifier (TF-IDF+LR or DistilBERT)."""
    # TODO: Vectorize texts, map labels to multi-hot, and fit classifier.
    raise NotImplementedError("TODO: implement training pipeline")


def predict_tags(
    prompt: str,
    model,
    tag_dictionary: Sequence[str],
    threshold: float = 0.5,
) -> list[TagPrediction]:
    """Predict tags from a prompt using a pre-trained classifier."""
    # TODO: Run model inference, threshold scores, and map to TagPrediction.
    raise NotImplementedError("TODO: implement inference")


def filter_tags(predictions: Iterable[TagPrediction], top_k: int | None = None) -> list[TagPrediction]:
    """Filter predictions to a stable top-k or thresholded list."""
    # TODO: Sort by score and optionally keep top_k.
    raise NotImplementedError("TODO: implement filtering")
