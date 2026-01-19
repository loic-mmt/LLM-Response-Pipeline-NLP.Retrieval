import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

EMB_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
PROJECT_ROOT = Path(__file__).resolve().parents[1]

def load_jsonl(path: Path):
    items = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items

def profile_text(m: dict) -> str:
    # Encodage des tags et triggers
    tags = m.get("tags", [])
    triggers = m.get("triggers", [])
    return " | ".join(tags + triggers)

def main():
    meta_path = PROJECT_ROOT / "memes" / "metadata.jsonl"
    out_dir = PROJECT_ROOT / "indexes"
    out_dir.mkdir(exist_ok=True)

    memes = load_jsonl(meta_path)
    model = SentenceTransformer(EMB_MODEL)

    texts = [profile_text(m) for m in memes]
    emb = model.encode(texts, normalize_embeddings=True)

    np.save(out_dir / "meme_emb.npy", emb)
    (out_dir / "meme_ids.json").write_text(
        json.dumps([m["id"] for m in memes], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Indexed {len(memes)} memes -> {out_dir}.")

if __name__ == "__main__":
    main()
