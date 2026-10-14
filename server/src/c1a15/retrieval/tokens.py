import re

_WORD = re.compile(r"[0-9A-Za-z가-힣._%-]+")
_HANGUL = re.compile(r"[가-힣]")


def tokenize(text: str) -> list[str]:
    """R3 토큰 = 공백 단위 단어 + 한글 2-gram(실행 해석 ⑤: EP-C1-FUSE-001 '글자 2-gram'과 함께 만족)."""
    tokens: list[str] = []
    for word in _WORD.findall(text or ""):
        tokens.append(word.lower())
        if _HANGUL.search(word) and len(word) > 2:
            tokens.extend(word[i : i + 2] for i in range(len(word) - 1))
    return tokens
