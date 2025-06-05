import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

import spacy

# 英語モデルを読み込む
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # モデルがインストールされていない場合
    nlp = spacy.blank("en")

NEGATIONS = {"no", "not", "without", "n't"}

CATEGORIES_ORDER = [
    "person",
    "hair",
    "eyes",
    "emotion",
    "position",
    "clothing",
    "accessory",
    "object",
    "animal",
    "environment",
    "misc",
]


def load_tags(path: Path) -> Tuple[Dict[str, Dict[str, str]], Dict[str, Dict[str, str]]]:
    """JSON ファイルからタグ辞書を読み込む"""
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("words", {}), data.get("phrases", {})


def is_negated(token) -> bool:
    """トークンが文中で否定されている場合 True を返す"""
    if token.i > 0 and token.doc[token.i - 1].lower_ in NEGATIONS:
        return True
    # 否定表現の子要素や祖先を確認する
    for child in token.children:
        if child.dep_ == "neg" or child.lower_ in NEGATIONS:
            return True
    for ancestor in token.ancestors:
        for child in ancestor.children:
            if child.dep_ == "neg" or child.lower_ in NEGATIONS:
                return True
    return False


def extract_tags(text: str, word_tags: Dict[str, Dict[str, str]], phrase_tags: Dict[str, Dict[str, str]]) -> List[Tuple[str, str]]:
    text_lower = text.lower()
    doc = nlp(text_lower)
    tokens_lower = [t.text.lower() for t in doc]
    used = set()
    tags: List[Tuple[str, str]] = []

    # フレーズは長いものから優先して処理する
    phrases_sorted = sorted(phrase_tags.items(), key=lambda x: len(x[0].split()), reverse=True)
    for phrase, info in phrases_sorted:
        phrase_tokens = phrase.split()
        length = len(phrase_tokens)
        for i in range(len(doc) - length + 1):
            if any((i + j) in used for j in range(length)):
                continue
            if tokens_lower[i:i + length] == phrase_tokens:
                if i > 0 and tokens_lower[i - 1] in NEGATIONS:
                    continue
                tags.append((info["tag"], info.get("category", "misc")))
                for j in range(length):
                    used.add(i + j)

    # 単語を処理する
    for i, token in enumerate(doc):
        if i in used:
            continue
        word = token.text.lower()
        if word in word_tags and not is_negated(token):
            info = word_tags[word]
            tags.append((info["tag"], info.get("category", "misc")))

    # 重複を除去する
    seen = set()
    unique_tags = []
    for tag, cat in tags:
        if tag not in seen:
            seen.add(tag)
            unique_tags.append((tag, cat))

    # カテゴリ順にソートする
    unique_tags.sort(key=lambda x: CATEGORIES_ORDER.index(x[1]) if x[1] in CATEGORIES_ORDER else len(CATEGORIES_ORDER))
    return unique_tags


def main() -> None:
    parser = argparse.ArgumentParser(description="自然文から danbooru タグを生成する")
    parser.add_argument("text", nargs="*", help="入力する説明文")
    parser.add_argument("--tags", default="tags.json", help="タグ定義 JSON のパス")
    args = parser.parse_args()

    if args.text:
        input_text = " ".join(args.text)
    else:
        input_text = input("説明文を入力してください: ")

    words, phrases = load_tags(Path(args.tags))
    extracted = extract_tags(input_text, words, phrases)
    output = ", ".join(tag for tag, _ in extracted)
    print(output)


if __name__ == "__main__":
    main()
