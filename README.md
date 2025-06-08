# Sunflower PDF Toolkit

PDFファイルを簡単に操作できるWebアプリケーションです。

## 機能

- PDFファイルのテキスト抽出
- 複数のPDFファイルの結合
- PDFファイルの分割
- PDFファイルの回転
- PDFファイルへの透かし追加

## インストール方法

1. リポジトリをクローン
```bash
git clone https://github.com/[your-username]/sunflower_pdf_toolkit.git
cd sunflower_pdf_toolkit
```

2. 仮想環境を作成して有効化
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. 依存関係のインストール
```bash
pip install -r requirements.txt
```

4. アプリケーションの実行
```bash
python app.py
```

## 使用方法

1. ブラウザで `http://localhost:5000` にアクセス
2. 必要な操作を選択し、PDFファイルをアップロード
3. 処理されたPDFファイルをダウンロード

## 注意事項

- アップロードできるファイルはPDFのみです
- アップロードされたファイルは一時的に保存され、処理後に削除されます

## ライセンス

MITライセンス 