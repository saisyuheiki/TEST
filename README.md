# タグ自動生成・変換ツール

Danbooru のタグは非常に数が多く、手作業で辞書を更新するのは大変です。本ツールは API から自動でタグ一覧を取得し、辞書を生成した上でキャプションからタグを抽出します。辞書更新の手間を大幅に削減することが目的です。

## インストール

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
sudo apt-get install mecab libmecab-dev mecab-ipadic-utf8
```

## 辞書の生成と更新

`build_tag_dict.py` を実行すると最新のタグを取得して `tags_en.json` と `tags_ja.json` を生成します。`tag_converter.py --update` を使うと自動でこのスクリプトが呼び出され、辞書が再作成されます。

```bash
python build_tag_dict.py              # 手動で生成
python tag_converter.py --update "a girl with blue eyes"  # 変換前に辞書更新
```

## 使い方

キャプションを英語または日本語で入力すると、対応する Danbooru タグを出力します。言語は `--lang` で指定できますが、`auto` にすると自動判定されます。

```bash
python tag_converter.py "A happy girl with long hair"
python tag_converter.py --lang ja "笑っている猫"
```

## ライセンスと注意事項

- 本ツールは MIT ライセンスです。
- Danbooru API は認証不要で利用できますが、過度なアクセスはレートリミットの対象となります。`build_tag_dict.py` は 0.3 秒待機しながら取得するため安全ですが、頻繁な実行は控えてください。

