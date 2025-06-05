"""Danbooru API からタグ一覧を取得して辞書を生成するスクリプト"""

from __future__ import annotations

import json
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, Tuple

import requests
from langdetect import detect
from nltk.corpus import wordnet as wn
from nltk.stem import PorterStemmer
from nltk import download as nltk_download
from fugashi import Tagger


API_URL = (
    "https://danbooru.donmai.us/tags.json?search[order]=count&limit=1000&page={}"
)

# WordNet の辞書が無ければダウンロードを試みる
try:
    wn.synsets("test")
except LookupError:
    nltk_download("wordnet", quiet=True)
    nltk_download("omw-1.4", quiet=True)


def fetch_all_tags() -> Iterable[dict]:
    """API からタグをすべて取得する"""
    page = 1
    while True:
        url = API_URL.format(page)
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            break
        for item in data:
            yield item
        page += 1
        time.sleep(0.3)


def classify(tag_name: str) -> str:
    """簡易的にカテゴリを推定する"""
    name = tag_name.lower()
    if "hair" in name:
        return "hair"
    if "eye" in name:
        return "eyes"
    if "pose" in name or "standing" in name or "sitting" in name:
        return "pose"
    if "smile" in name or "expression" in name:
        return "expression"
    if "background" in name or "sky" in name:
        return "background"
    if any(k in name for k in ["sword", "gun", "weapon", "book", "bag", "hat"]):
        return "item"
    return "misc"


def add_entry(dic: Dict[str, dict], key: str, tag: str, category: str, dup: Dict[str, int]) -> None:
    key_l = key.lower()
    if key_l in dic:
        dup["count"] += 1
    dic[key_l] = {"tag": tag, "category": category}


def build_dicts() -> Tuple[Dict[str, dict], Dict[str, dict], int]:
    """辞書を生成して返す"""
    tagger = Tagger()
    stemmer = PorterStemmer()
    en: Dict[str, dict] = {}
    ja: Dict[str, dict] = {}
    dup = {"count": 0}

    for tag in fetch_all_tags():
        if tag.get("category") != 0:
            continue
        name: str = tag["name"]
        ja_tr: str | None = tag.get("ja_translation")
        key_en = name.replace("_", " ")
        cat = classify(key_en)
        add_entry(en, key_en, name, cat, dup)
        add_entry(en, key_en.replace(" ", ""), name, cat, dup)

        if ja_tr:
            add_entry(ja, ja_tr, name, cat, dup)
            for token in tagger(ja_tr):
                lemma = token.dictionary_form
                if lemma and lemma != ja_tr:
                    add_entry(ja, lemma, name, cat, dup)

        words = key_en.split()
        stems = [stemmer.stem(w) for w in words]
        add_entry(en, " ".join(stems), name, cat, dup)
        try:
            for w in words:
                syns = wn.synsets(w)
                for syn in syns[:3]:
                    for lemma in syn.lemma_names()[:1]:
                        syn_words = [lemma if x == w else x for x in words]
                        add_entry(en, " ".join(syn_words).replace("_", " "), name, cat, dup)
        except Exception:
            pass

    return en, ja, dup["count"]


def main() -> None:
    en, ja, dup = build_dicts()
    Path("tags_en.json").write_text(
        json.dumps(en, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    Path("tags_ja.json").write_text(
        json.dumps(ja, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"英語タグ数: {len(en)} 日本語タグ数: {len(ja)} 重複数: {dup}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"エラーが発生しました: {e}", file=sys.stderr)
        sys.exit(1)
