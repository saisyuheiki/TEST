import argparse
import re

# 単語から danbooru タグへのマッピング
WORD_TAGS = {
    "girl": "1girl",
    "boy": "1boy",
    "smile": "smile",
    "smiling": "smile",
    "happy": "smile",
    "weapon": "weapon",
    "sword": "sword",
    "gun": "gun",
    "cat": "cat",
    "dog": "dog",
    "tree": "tree",
    "outdoor": "outdoors",
    "indoor": "indoors",
    "standing": "standing",
    "sitting": "sitting",
    "blush": "blush",
    "blushing": "blush",
}

# 複数語フレーズから danbooru タグへのマッピング
PHRASE_TAGS = {
    "long hair": "long_hair",
    "short hair": "short_hair",
    "blue eyes": "blue_eyes",
    "red eyes": "red_eyes",
    "green eyes": "green_eyes",
    "black hair": "black_hair",
    "brown hair": "brown_hair",
    "blonde hair": "blonde_hair",
}

def generate_prompt(text: str) -> str:
    """入力テキストを danbooru タグのカンマ区切りリストに変換する"""
    text = text.lower()
    tags = []

    # 最初にフレーズを検出する
    for phrase, tag in PHRASE_TAGS.items():
        if phrase in text:
            tags.append(tag)
            text = text.replace(phrase, " ")

    # 単語を処理する
    tokens = re.findall(r"\b\w+\b", text)
    for token in tokens:
        if token in WORD_TAGS:
            tags.append(WORD_TAGS[token])

    # 順序を保ったまま重複を除去する
    seen = set()
    unique_tags = []
    for tag in tags:
        if tag not in seen:
            seen.add(tag)
            unique_tags.append(tag)

    return ", ".join(unique_tags)


def main() -> None:
    parser = argparse.ArgumentParser(description="Stable Diffusion 用の danbooru タグへ変換する")
    parser.add_argument("text", nargs="*", help="入力する説明文")
    args = parser.parse_args()

    if args.text:
        input_text = " ".join(args.text)
    else:
        input_text = input("説明文を入力してください: ")

    prompt = generate_prompt(input_text)
    print(prompt)


if __name__ == "__main__":
    main()
