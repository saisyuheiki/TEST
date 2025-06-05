"""英語または日本語のキャプションを Danbooru タグへ変換する。"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List

import spacy
from langdetect import detect


@dataclass
class TagEntry:
    tag: str
    category: str = "misc"


CATEGORY_ORDER: List[str] = [
    "count/people",
    "gender",
    "hair",
    "eyes",
    "expression",
    "pose/action",
    "clothing",
    "background/setting",
    "misc",
]

NEGATIONS = {
    "not",
    "no",
    "n't",
    "never",
    "ない",
    "ぬ",
    "ず",
    "ません",
    "じゃない",
    "ではない",
}


def load_dicts(en_path: Path, ja_path: Path) -> Dict[str, TagEntry]:
    """JSON ファイルからタグ辞書を読み込み統合する。"""

    def _load(path: Path) -> Dict[str, TagEntry]:
        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError as e:
            raise SystemExit(f"辞書ファイルが見つかりません: {path}") from e
        except json.JSONDecodeError as e:
            raise SystemExit(f"{path} の JSON が不正です: {e}") from e
        result: Dict[str, TagEntry] = {}
        for key, value in data.items():
            if not isinstance(value, dict) or "tag" not in value:
                continue
            result[key.lower()] = TagEntry(
                tag=value["tag"],
                category=value.get("category", "misc"),
            )
        return result

    tags = {}
    tags.update(_load(en_path))
    tags.update(_load(ja_path))
    return tags


def detect_lang(text: str) -> str:
    """言語判定により 'en' または 'ja' を返す。"""
    try:
        code = detect(text)
    except Exception:
        return "en"
    return "ja" if code.startswith("ja") else "en"


def load_model(lang: str) -> spacy.language.Language:
    """spaCy モデルを読み込む。"""
    model_name = "en_core_web_sm" if lang == "en" else "ja_core_news_sm"
    try:
        return spacy.load(model_name)
    except Exception as e:
        raise SystemExit(
            f"spaCy のモデル '{model_name}' が見つかりません。'python -m spacy download {model_name}' でインストールしてください。"
        ) from e


def tokenise(
    text: str,
    lang: str,
    nlp_en: spacy.language.Language,
    nlp_ja: spacy.language.Language,
) -> tuple[spacy.tokens.Doc, List[str]]:
    """テキストを解析して語形素を取得する。"""
    nlp = nlp_en if lang == "en" else nlp_ja
    doc = nlp(text)
    lemmas = [tok.lemma_.lower() if tok.lemma_ else tok.text.lower() for tok in doc]
    return doc, lemmas


def extract_tags(
    doc: spacy.tokens.Doc, lemmas: List[str], mapping: Dict[str, TagEntry]
) -> List[TagEntry]:
    """フレーズ優先でタグを抽出する。"""
    used: set[int] = set()
    tags: List[TagEntry] = []

    items = sorted(mapping.items(), key=lambda kv: len(kv[0].split()), reverse=True)
    for phrase, info in items:
        tokens = phrase.lower().split()
        length = len(tokens)
        for i in range(len(lemmas) - length + 1):
            if any((i + j) in used for j in range(length)):
                continue
            if lemmas[i : i + length] == tokens:
                if i > 0 and lemmas[i - 1] in NEGATIONS:
                    continue
                tags.append(info)
                used.update(range(i, i + length))
    return tags


def order_tags(tags: Iterable[TagEntry]) -> List[str]:
    """カテゴリを考慮してタグを並べ替える。"""
    seen: set[str] = set()
    unique: List[TagEntry] = []
    for entry in tags:
        if entry.tag not in seen:
            seen.add(entry.tag)
            unique.append(entry)

    priority = {cat: i for i, cat in enumerate(CATEGORY_ORDER)}
    unique.sort(key=lambda t: priority.get(t.category, priority["misc"]))
    return [t.tag for t in unique]


def main() -> None:
    """コマンドライン引数を解析して処理を実行する。"""
    parser = argparse.ArgumentParser(description="キャプションから Danbooru タグを生成")
    parser.add_argument("caption", nargs="*", help="入力するキャプション")
    parser.add_argument(
        "--lang", choices=["en", "ja", "auto"], default="auto", help="入力言語"
    )
    parser.add_argument(
        "--en_dict", default="tags_en.json", help="英語タグ辞書へのパス"
    )
    parser.add_argument(
        "--ja_dict", default="tags_ja.json", help="日本語タグ辞書へのパス"
    )
    args = parser.parse_args()

    text = " ".join(args.caption) if args.caption else input("> ")
    lang = detect_lang(text) if args.lang == "auto" else args.lang

    nlp_en = load_model("en")
    nlp_ja = load_model("ja")

    mapping = load_dicts(Path(args.en_dict), Path(args.ja_dict))

    doc, lemmas = tokenise(text, lang, nlp_en, nlp_ja)
    tags = extract_tags(doc, lemmas, mapping)
    ordered = order_tags(tags)
    print(", ".join(ordered))


if __name__ == "__main__":
    main()
