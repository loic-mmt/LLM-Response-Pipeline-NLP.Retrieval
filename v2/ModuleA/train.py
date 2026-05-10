from __future__ import annotations

import argparse
import json
import pickle
from pathlib import Path
from typing import Any
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from v2.ModuleA.classifier import (
    GroupedClassifier,
    load_tag_groups,
    train_grouped_classifiers,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train ModuleA grouped tag classifier.")
    parser.add_argument(
        "--dataset",
        required=True,
        help="Path to training data (.jsonl or .json list).",
    )
    parser.add_argument(
        "--tags-path",
        default="tags.jsonl",
        help="Path to tag groups file.",
    )
    parser.add_argument(
        "--output",
        default="v2/ModuleA/models/grouped_classifier.pkl",
        help="Output pickle artifact path.",
    )
    return parser.parse_args()


def _read_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"dataset not found: {path}")

    if path.suffix.lower() == ".jsonl":
        rows: list[dict[str, Any]] = []
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
                    raise ValueError(f"line {line_no}: expected JSON object")
                rows.append(obj)
        return rows

    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list) or not all(isinstance(x, dict) for x in raw):
        raise ValueError("JSON dataset must be a list of objects")
    return raw


def _require_list_of_str(value: Any, field: str, row_idx: int) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(x, str) for x in value):
        raise ValueError(f"row {row_idx}: '{field}' must be a list[str]")
    return [x.strip().lower() for x in value if x.strip()]


def _require_str(value: Any, field: str, row_idx: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"row {row_idx}: '{field}' must be a non-empty string")
    return value.strip().lower()


def load_training_dataset(path: str) -> tuple[list[str], list[dict[str, object]]]:
    """Load training rows expected by `train_grouped_classifiers`."""
    rows = _read_rows(Path(path))
    texts: list[str] = []
    labels: list[dict[str, object]] = []

    for idx, row in enumerate(rows, start=1):
        text_value = row.get("text", row.get("prompt"))
        if not isinstance(text_value, str) or not text_value.strip():
            raise ValueError(f"row {idx}: expected non-empty 'text' (or 'prompt')")

        texts.append(text_value.strip())
        labels.append(
            {
                "tags_ton": _require_list_of_str(row.get("tags_ton"), "tags_ton", idx),
                "tags_act": _require_list_of_str(row.get("tags_act"), "tags_act", idx),
                "tags_intensity": _require_str(row.get("tags_intensity"), "tags_intensity", idx),
                "tags_format": _require_str(row.get("tags_format"), "tags_format", idx),
            }
        )

    if not texts:
        raise ValueError("dataset is empty")
    return texts, labels


def save_model_artifact(path: str, model: GroupedClassifier, tag_groups: dict[str, list[str]], n_samples: int) -> None:
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "model": model,
        "tag_groups": tag_groups,
        "n_samples": n_samples,
    }
    with out_path.open("wb") as f:
        pickle.dump(payload, f)


def main() -> None:
    args = parse_args()

    texts, labels = load_training_dataset(args.dataset)
    tag_groups = load_tag_groups(args.tags_path)
    model = train_grouped_classifiers(texts=texts, labels=labels, tag_groups=tag_groups)

    save_model_artifact(args.output, model=model, tag_groups=tag_groups, n_samples=len(texts))
    print(f"Trained GroupedClassifier on {len(texts)} samples -> {args.output}")


if __name__ == "__main__":
    main()
