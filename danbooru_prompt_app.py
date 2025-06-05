import argparse
import re

# Mapping from words to danbooru tags
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

# Mapping from multi-word phrases to danbooru tags
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
    """Convert input text to a comma-separated list of danbooru tags."""
    text = text.lower()
    tags = []

    # Detect phrases first
    for phrase, tag in PHRASE_TAGS.items():
        if phrase in text:
            tags.append(tag)
            text = text.replace(phrase, " ")

    # Process single words
    tokens = re.findall(r"\b\w+\b", text)
    for token in tokens:
        if token in WORD_TAGS:
            tags.append(WORD_TAGS[token])

    # Remove duplicates while preserving order
    seen = set()
    unique_tags = []
    for tag in tags:
        if tag not in seen:
            seen.add(tag)
            unique_tags.append(tag)

    return ", ".join(unique_tags)


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert text to danbooru tags for Stable Diffusion prompts")
    parser.add_argument("text", nargs="*", help="Input description")
    args = parser.parse_args()

    if args.text:
        input_text = " ".join(args.text)
    else:
        input_text = input("Enter description: ")

    prompt = generate_prompt(input_text)
    print(prompt)


if __name__ == "__main__":
    main()

