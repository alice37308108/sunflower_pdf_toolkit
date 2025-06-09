# 🌻 Sunflower PDF Toolkit

PDFファイル処理Webアプリケーションです。直感的な操作で様々なPDF処理を行うことができます。

## ✨ 機能

### 📄 基本機能
- **PDF結合**: 複数のPDFファイルを好きな順番で結合
- **PDF分割**: 指定したページ範囲でPDFを分割
- **PDF回転**: 全ページまたは特定のページを回転
- **ページ削除**: 不要なページを削除
- **画像透かし**: PNG、JPG、JPEG、GIF、BMP、PDF画像を透かしとして追加

## 🚀 インストール方法

1. **リポジトリをクローン**
```bash
git clone https://github.com/[your-username]/sunflower_pdf_toolkit.git
cd sunflower_pdf_toolkit
```

2. **仮想環境を作成して有効化**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. **依存関係のインストール**
```bash
pip install -r requirements.txt
```

4. **アプリケーションの実行**
```bash
python app.py
```

## 📖 使用方法

### 基本的な流れ
1. ブラウザで `http://localhost:5000` にアクセス
2. 処理したい操作のボタンをクリック（🔗結合、✂️分割、🔄回転、🗑️削除、🏷️透かし）
3. 必要なファイルをアップロード
4. 設定を行い、処理を実行
5. プレビューで確認後、ダウンロード

### 各機能の詳細

#### 🔗 PDF結合
- 複数のPDFファイルを選択
- ドラッグ&ドロップまたは↑↓ボタンで順番を調整
- ✕ボタンで不要なファイルを削除

#### ✂️ PDF分割
- メインPDFファイルを選択
- ページ範囲を指定（例: `1-3,5,7-9`）

#### 🔄 PDF回転
- メインPDFファイルを選択
- 回転角度を選択（90°、180°、270°）
- 全ページまたは特定ページを選択

#### 🗑️ ページ削除
- メインPDFファイルを選択
- 削除するページを指定（例: `1,3,5-7`）

#### 🏷️ 透かし追加
- メインPDFファイルを選択
- 透かし用ファイルを選択（PNG、JPG等）
- 自動的に透明度とサイズが調整されます

## 🛠️ 技術仕様

### 使用技術
- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **PDF処理**: PyPDF2
- **画像処理**: Pillow (PIL)
- **PDF生成**: ReportLab
- **PDFビューアー**: PDF.js

### 対応ファイル形式
- **PDF入力**: .pdf
- **透かし画像**: .png, .jpg, .jpeg, .gif, .bmp

## ⚠️ 注意事項

- アップロードできるファイルサイズに制限があります
- アップロードされたファイルは処理後に自動削除されます
- 大きなPDFファイルの処理には時間がかかる場合があります
- ブラウザはモダンなものをご利用ください（Chrome、Firefox、Safari、Edge推奨）

## 🔧 開発者向け情報

### プロジェクト構造
```
sunflower_pdf_toolkit/
├── app.py                 # メインアプリケーション
├── templates/
│   └── index.html        # フロントエンドHTML
├── uploads/              # 一時ファイル保存ディレクトリ
├── requirements.txt      # Python依存関係
└── README.md            # このファイル
```

### 主要な関数
- `is_valid_pdf()`: PDFファイル検証
- `is_valid_image()`: 画像ファイル検証
- `create_watermark_pdf_from_image()`: 画像から透かしPDF作成


---
