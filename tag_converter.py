"""英語または日本語のキャプションを Danbooru タグへ変換する。"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import ujson as json

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


def load_dicts(en_path: Path, ja_path: Path) -> Tuple[Dict[Tuple[str, ...], TagEntry], int]:
    """JSON ファイルからタグ辞書を読み込み統合する。"""

    def _load(path: Path) -> Dict[Tuple[str, ...], TagEntry]:
        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError as e:
            raise SystemExit(f"辞書ファイルが見つかりません: {path}") from e
        except ValueError as e:
            raise SystemExit(f"{path} の JSON が不正です: {e}") from e
        result: Dict[Tuple[str, ...], TagEntry] = {}
        for key, value in data.items():
            if not isinstance(value, dict) or "tag" not in value:
                continue
            tokens = tuple(key.lower().split())
            result[tokens] = TagEntry(
                tag=value["tag"],
                category=value.get("category", "misc"),
            )
        return result

    mapping: Dict[Tuple[str, ...], TagEntry] = {}
    mapping.update(_load(en_path))
    mapping.update(_load(ja_path))
    max_len = max((len(k) for k in mapping.keys()), default=1)
    return mapping, max_len


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
    lemmas: List[str], mapping: Dict[Tuple[str, ...], TagEntry], max_len: int
) -> List[TagEntry]:
    """辞書を用いてタグを抽出する。"""
    used: set[int] = set()
    tags: List[TagEntry] = []

    n = len(lemmas)
    for i in range(n):
        if i in used:
            continue
        for length in range(max_len, 0, -1):
            if i + length > n:
                continue
            key = tuple(lemmas[i : i + length])
            entry = mapping.get(key)
            if entry is None:
                continue
            if i > 0 and lemmas[i - 1] in NEGATIONS:
                continue
            tags.append(entry)
            used.update(range(i, i + length))
            break
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
    parser.add_argument("--update", action="store_true", help="辞書を再生成する")
    args = parser.parse_args()

    if args.update:
        try:
            subprocess.run([sys.executable, "build_tag_dict.py"], check=True)
        except Exception as e:
            print(f"辞書更新に失敗しました: {e}", file=sys.stderr)
            sys.exit(1)

    text = " ".join(args.caption) if args.caption else input("> ")
    lang = detect_lang(text) if args.lang == "auto" else args.lang

    nlp_en = load_model("en")
    nlp_ja = load_model("ja")

    mapping, max_len = load_dicts(Path(args.en_dict), Path(args.ja_dict))

    doc, lemmas = tokenise(text, lang, nlp_en, nlp_ja)
    tags = extract_tags(lemmas, mapping, max_len)
    ordered = order_tags(tags)
    print(", ".join(ordered))


if __name__ == "__main__":
    main()
