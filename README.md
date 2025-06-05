# TEST

テスト

This repository contains a simple script to help generate Stable Diffusion prompts using danbooru-style tags.

## Usage

There are two scripts available:

1. **danbooru_prompt_app.py** - A basic word/phrase matcher.
2. **tag_converter.py** - A spaCy based converter that reads tags from `tags.json`.

Run the new converter with a description of the desired image:

```bash
python tag_converter.py "A happy girl with blue eyes and long hair"
```

The script will output a comma-separated list of tags that can be used as a prompt for Stable Diffusion.
