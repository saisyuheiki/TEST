# TEST

このリポジトリには、danbooru 形式のタグを用いて Stable Diffusion 向けプロンプトを生成するスクリプトが含まれています。

## 使い方

利用できるスクリプトは次の 2 つです。

1. **danbooru_prompt_app.py** - 単純な単語やフレーズを置き換えるだけの変換ツール。
2. **tag_converter.py** - `tags.json` を読み込み、spaCy で英文を解析してタグを抽出します。

### tag_converter.py の実行例

```bash
python tag_converter.py "A happy girl with blue eyes and long hair"
```

実行すると、使用可能なタグがカンマ区切りで表示されます。
事前に `pip install spacy` と `python -m spacy download en_core_web_sm` を実行して spaCy と英語モデルをインストールしてください。
