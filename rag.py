"""Small, dependency-free retrieval for the investigator knowledge base."""

import re
from pathlib import Path


def _words(text):
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def load_sections(directory=None):
    """Load Markdown headings and their following paragraphs."""
    directory = Path(directory or Path(__file__).parent / "knowledge")
    sections = []
    for path in sorted(directory.glob("*.md")):
        heading = None
        body = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("## "):
                if heading and body:
                    sections.append(
                        (f"{path.stem}:{heading}", "\n".join(body))
                    )
                heading = line[3:].strip()
                body = []
            elif heading and line.strip():
                body.append(line.strip())
        if heading and body:
            sections.append((f"{path.stem}:{heading}", "\n".join(body)))
    return sections


def retrieve(query, limit=3, directory=None):
    """Return highest-overlap sections and stable source IDs."""
    query_words = _words(query)
    scored = []
    for source_id, text in load_sections(directory):
        score = len(query_words & _words(text))
        if score:
            scored.append((score, source_id, text))
    scored.sort(key=lambda item: (-item[0], item[1]))
    return [
        {"source_id": source, "text": text}
        for _, source, text in scored[:limit]
    ]
