from typing import List

def split_into_paragraphs(text: str) -> List[str]:
    parts = [p.strip() for p in text.split("\n\n")]
    return [p for p in parts if p]
