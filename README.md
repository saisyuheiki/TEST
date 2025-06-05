# タグ変換ツール

`tag_converter.py` は英語または日本語のキャプションを Danbooru タグの一覧に変換します。

## インストール

1. Python 3.9 以降を用意してください。
2. 必要なパッケージをインストールします。
   ```bash
   pip install spacy langdetect
   python -m spacy download en_core_web_sm
   python -m spacy download ja_core_news_sm
   ```

## 使い方

キャプションをコマンドライン引数で渡すか、指定しない場合は標準入力から入力します。

```bash
python tag_converter.py "A happy girl with long hair and blue eyes"
python tag_converter.py --lang auto "笑顔の茶髪の女の子"
```

実行すると、対応する Danbooru タグをカンマ区切りで表示します。

### 辞書の拡張

タグの定義は `tags_en.json` と `tags_ja.json` にあります。各エントリは単語やフレーズ（小文字）を Danbooru タグと任意のカテゴリに対応させます。

```json
{
  "long hair": {"tag": "long_hair", "category": "hair"}
}
```

新しい単語やフレーズを認識させたい場合は、これらのファイルに追記してください。
