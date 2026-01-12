import json, re
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer

from src.llm.client import OllamaClient
from src.render import draw_bottom_caption

EMB_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
TOPK = 8

def normalize(t: str) ->str:
    t = t.lower().strip()
    t = re.sub(r"[^\w\s']", " ", t)
    t = re.sub(r"\s+", " ", t)
    return t

def load_memes():
    memes = []
    with open("memes/metadata.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                memes.append(json.load(line))
    by_id = {m["id"]: m for m in memes}
    return memes, by_id


def rule_match(prompt_norm: str, memes):
    for m in memes:
        for trig in m.get("triggers", []):
            if normalize(trig) in prompt_norm:
                return m["id"]
    return None


def topk_by_embeddings(prompt_norm: str, k: int =  TOPK):
    emb = np.load("indexes/memes_emb.npy")
    ids = json.loads(Path("indexes/meme_ids.json").read_text(encoding="utf-8"))

    model = SentenceTransformer(EMB_MODEL)
    q = model.encode([prompt_norm], normalize_embeddings=True)[0]
    scores = emb @ q
    idxs = np.argsort(-scores)[:k]
    return [(ids[i], float(scores[i])) for i in idxs]


def caption_with_llm(client: OllamaClient, user_prompt: str, meme: dict) -> str:
    tags = meme.get("tags", [])
    prompt = f"""
Return ONLY JSON: {{"caption":"..."}}.

Rules:
- English unless the user prompt is clearly French.
- Max 80 characters.
- No emojis.
- Match the vibe tags: {tags}
- Make it meme-like: short, punchy.

USER_PROMPT: {user_prompt}
"""
    raw = client.complete(prompt, temperature=0.2, max_tokens=160).strip()

    try:
        s = raw[raw.find("{"):raw.rfind("}")+1]
        obj = json.loads(s)
        cap = (obj.get("caption") or "").strip()
        if not cap:
            return "..."
        return cap[:80]
    except Exception:
        return "..."
    
