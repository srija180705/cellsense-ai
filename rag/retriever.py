"""
Lightweight retrieval over the maintenance knowledge base.

Uses TF-IDF (scikit-learn) so it runs offline with zero downloads. The corpus is
split into sections (by markdown '##' headings); each section is a citable chunk.
Swap in sentence-transformer embeddings + a vector DB later without changing the
retrieve() interface.
"""
import re
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

CORPUS_DIR = Path(__file__).resolve().parent / "corpus"


def _load_chunks():
    chunks = []
    for f in sorted(CORPUS_DIR.glob("*.md")):
        if f.name.lower() == "readme.md":
            continue
        text = f.read_text(encoding="utf-8")
        lines = text.splitlines()
        title = lines[0].lstrip("# ").strip() if lines and lines[0].startswith("#") else f.stem
        # Split into sections on '## ' headings
        sections = re.split(r"\n##\s+", text)
        for i, part in enumerate(sections):
            plines = part.splitlines()
            if i == 0:
                section = "Overview"
                body = "\n".join(plines[1:]).strip()  # drop the '# Title' line
            else:
                section = plines[0].strip()
                body = "\n".join(plines[1:]).strip()
            if body:
                chunks.append({"doc": title, "section": section, "text": body})
    return chunks


_CHUNKS = _load_chunks()
_TEXTS = [f"{c['doc']} {c['section']} {c['text']}" for c in _CHUNKS]
_VECTORIZER = TfidfVectorizer(stop_words="english")
_MATRIX = _VECTORIZER.fit_transform(_TEXTS) if _TEXTS else None


def retrieve(query: str, k: int = 3):
    """Return up to k relevant chunks: {source, snippet, score}."""
    if _MATRIX is None:
        return []
    qv = _VECTORIZER.transform([query])
    sims = linear_kernel(qv, _MATRIX).flatten()
    order = sims.argsort()[::-1][:k]
    out = []
    for i in order:
        if sims[i] <= 0:
            continue
        c = _CHUNKS[i]
        snippet = c["text"].replace("\n", " ")
        out.append({
            "source": f"{c['doc']} § {c['section']}",
            "snippet": snippet[:240] + ("…" if len(snippet) > 240 else ""),
            "score": round(float(sims[i]), 3),
        })
    return out


def corpus_size():
    return len(_CHUNKS)
