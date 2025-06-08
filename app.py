from flask import Flask, request, render_template, send_file, jsonify
from PyPDF2 import PdfReader, PdfWriter, PdfMerger
import os
from dotenv import load_dotenv
import io
from werkzeug.utils import secure_filename

app = Flask(__name__)
load_dotenv()

# アップロードされたファイルの保存先
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def is_valid_pdf(file):
    try:
        reader = PdfReader(file)
        # ファイルポインタを先頭に戻す
        file.seek(0)
        return True
    except Exception:
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'ファイルがありません'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'ファイルが選択されていません'}), 400
        
        if not file.filename.endswith('.pdf'):
            return jsonify({'error': 'PDFファイルのみ対応しています'}), 400

        if not is_valid_pdf(file):
            return jsonify({'error': 'PDFファイルの読み込みに失敗しました。ファイルが破損しているか、正しいPDF形式ではありません。'}), 400
        
        filepath = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
        file.save(filepath)
        
        # PDFの情報を取得
        reader = PdfReader(filepath)
        info = {
            'ページ数': len(reader.pages),
            'ファイル名': file.filename,
            'ファイルサイズ': os.path.getsize(filepath)
        }
        return jsonify(info)
    except Exception as e:
        return jsonify({'error': f'PDFの処理中にエラーが発生しました: {str(e)}'}), 500

@app.route('/extract-text', methods=['POST'])
def extract_text():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'ファイルがありません'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'ファイルが選択されていません'}), 400

        if not file.filename.endswith('.pdf'):
            return jsonify({'error': 'PDFファイルのみ対応しています'}), 400

        if not is_valid_pdf(file):
            return jsonify({'error': 'PDFファイルの読み込みに失敗しました。ファイルが破損しているか、正しいPDF形式ではありません。'}), 400

        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n\n"
        return jsonify({'text': text})
    except Exception as e:
        return jsonify({'error': f'テキスト抽出中にエラーが発生しました: {str(e)}'}), 500

@app.route('/merge-pdfs', methods=['POST'])
def merge_pdfs():
    try:
        if 'files[]' not in request.files:
            return jsonify({'error': 'ファイルがありません'}), 400

        files = request.files.getlist('files[]')
        if not files or files[0].filename == '':
            return jsonify({'error': 'ファイルが選択されていません'}), 400

        # すべてのファイルがPDFであることを確認
        for file in files:
            if not file.filename.endswith('.pdf'):
                return jsonify({'error': 'すべてのファイルがPDF形式である必要があります'}), 400
            if not is_valid_pdf(file):
                return jsonify({'error': f'ファイル "{file.filename}" の読み込みに失敗しました。ファイルが破損しているか、正しいPDF形式ではありません。'}), 400

        merger = PdfMerger()
        
        for file in files:
            merger.append(file)
        
        output = io.BytesIO()
        merger.write(output)
        output.seek(0)
        
        return send_file(
            output,
            download_name='merged.pdf',
            as_attachment=True,
            mimetype='application/pdf'
        )
    except Exception as e:
        return jsonify({'error': f'PDF結合中にエラーが発生しました: {str(e)}'}), 500

@app.route('/split-pdf', methods=['POST'])
def split_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'ファイルがありません'}), 400

        file = request.files['file']
        split_pages_str = request.form.get('split_pages', '')
        
        if file.filename == '' or not split_pages_str.strip():
            return jsonify({'error': 'ファイルまたはページ範囲が指定されていません'}), 400
            
        page_ranges = split_pages_str.split(',')

        if not file.filename.endswith('.pdf'):
            return jsonify({'error': 'PDFファイルのみ対応しています'}), 400

        if not is_valid_pdf(file):
            return jsonify({'error': 'PDFファイルの読み込みに失敗しました。ファイルが破損しているか、正しいPDF形式ではありません。'}), 400

        reader = PdfReader(file)
        writer = PdfWriter()
        
        # ページ範囲を解析して有効なページを追加
        valid_pages = set()
        for page_range in page_ranges:
            try:
                if '-' in page_range:
                    start, end = map(int, page_range.strip().split('-'))
                    # 範囲の妥当性チェック
                    if start < 1 or end > len(reader.pages) or start > end:
                        continue
                    valid_pages.update(range(start-1, end))
                else:
                    page_num = int(page_range.strip()) - 1
                    if 0 <= page_num < len(reader.pages):
                        valid_pages.add(page_num)
            except ValueError:
                continue
        
        # ページが選択されていない場合はエラー
        if not valid_pages:
            return jsonify({'error': '有効なページが指定されていません'}), 400
        
        # 選択されたページを順番に追加
        for page_num in sorted(valid_pages):
            writer.add_page(reader.pages[page_num])
        
        output = io.BytesIO()
        writer.write(output)
        output.seek(0)
        
        # 元のファイル名を基に新しいファイル名を生成
        original_name = os.path.splitext(file.filename)[0]
        new_filename = f'{original_name}_split.pdf'
        
        return send_file(
            output,
            download_name=new_filename,
            as_attachment=True,
            mimetype='application/pdf'
        )
    except Exception as e:
        return jsonify({'error': f'PDF分割中にエラーが発生しました: {str(e)}'}), 500

@app.route('/rotate-pdf', methods=['POST'])
def rotate_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'ファイルがありません'}), 400

        file = request.files['file']
        rotation = int(request.form.get('rotation', 90))
        rotate_type = request.form.get('rotate_type', 'all')
        pages = request.form.get('rotate_pages', '')
        
        # デバッグ情報
        print(f"回転度数: {rotation}, 回転タイプ: {rotate_type}, ページ: '{pages}'")
        print(f"受信したフォームデータ: {dict(request.form)}")
        
        if file.filename == '':
            return jsonify({'error': 'ファイルが選択されていません'}), 400

        if not file.filename.endswith('.pdf'):
            return jsonify({'error': 'PDFファイルのみ対応しています'}), 400

        if not is_valid_pdf(file):
            return jsonify({'error': 'PDFファイルの読み込みに失敗しました。ファイルが破損しているか、正しいPDF形式ではありません。'}), 400

        reader = PdfReader(file)
        writer = PdfWriter()
        
        if rotate_type == 'all':
            # すべてのページを回転
            for i, page in enumerate(reader.pages):
                # ページのコピーを作成して回転
                new_page = page
                new_page = new_page.rotate(rotation)
                writer.add_page(new_page)
        else:
            # 特定のページが選択されている場合、ページ指定が必須
            if not pages.strip():
                return jsonify({'error': '特定のページを選択した場合は、ページ範囲を指定してください'}), 400
                
            try:
                # ページ範囲を解析（例: "1-3,5,7-9"）
                selected_pages = set()
                for part in pages.split(','):
                    part = part.strip()
                    if not part:
                        continue
                    if '-' in part:
                        start, end = map(int, part.split('-'))
                        if start < 1 or end > len(reader.pages) or start > end:
                            continue
                        selected_pages.update(range(start-1, end))
                    else:
                        page_num = int(part) - 1
                        if 0 <= page_num < len(reader.pages):
                            selected_pages.add(page_num)
                
                # 有効なページが選択されているかチェック
                if not selected_pages:
                    return jsonify({'error': '有効なページ範囲が指定されていません'}), 400
                
                # ページを処理
                for i in range(len(reader.pages)):
                    page = reader.pages[i]
                    if i in selected_pages:
                        # 選択されたページを回転
                        new_page = page.rotate(rotation)
                        writer.add_page(new_page)
                    else:
                        # 選択されていないページはそのまま追加
                        writer.add_page(page)
                        
            except ValueError:
                return jsonify({'error': '無効なページ範囲が指定されました'}), 400
        
        output = io.BytesIO()
        writer.write(output)
        output.seek(0)
        
        # 元のファイル名を基に新しいファイル名を生成
        original_name = os.path.splitext(file.filename)[0]
        new_filename = f'{original_name}_rotated.pdf'
        
        return send_file(
            output,
            download_name=new_filename,
            as_attachment=True,
            mimetype='application/pdf'
        )
    except Exception as e:
        return jsonify({'error': f'PDF回転中にエラーが発生しました: {str(e)}'}), 500

@app.route('/add-watermark', methods=['POST'])
def add_watermark():
    try:
        if 'file' not in request.files or 'watermark' not in request.files:
            return jsonify({'error': 'メインファイルまたは透かしファイルがありません'}), 400

        file = request.files['file']
        watermark = request.files['watermark']
        
        if file.filename == '' or watermark.filename == '':
            return jsonify({'error': 'ファイルが選択されていません'}), 400

        if not file.filename.endswith('.pdf') or not watermark.filename.endswith('.pdf'):
            return jsonify({'error': 'PDFファイルのみ対応しています'}), 400

        if not is_valid_pdf(file):
            return jsonify({'error': 'メインPDFファイルの読み込みに失敗しました。ファイルが破損しているか、正しいPDF形式ではありません。'}), 400

        if not is_valid_pdf(watermark):
            return jsonify({'error': '透かしPDFファイルの読み込みに失敗しました。ファイルが破損しているか、正しいPDF形式ではありません。'}), 400

        reader = PdfReader(file)
        watermark_reader = PdfReader(watermark)
        writer = PdfWriter()
        
        watermark_page = watermark_reader.pages[0]
        
        for page in reader.pages:
            page.merge_page(watermark_page)
            writer.add_page(page)
        
        output = io.BytesIO()
        writer.write(output)
        output.seek(0)
        
        return send_file(
            output,
            download_name='watermarked.pdf',
            as_attachment=True,
            mimetype='application/pdf'
        )
    except Exception as e:
        return jsonify({'error': f'透かし追加中にエラーが発生しました: {str(e)}'}), 500

@app.route('/delete-pages', methods=['POST'])
def delete_pages():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'ファイルがありません'}), 400

        file = request.files['file']
        pages = request.form.get('delete_pages', '')
        
        if file.filename == '':
            return jsonify({'error': 'ファイルが選択されていません'}), 400

        if not file.filename.endswith('.pdf'):
            return jsonify({'error': 'PDFファイルのみ対応しています'}), 400

        if not is_valid_pdf(file):
            return jsonify({'error': 'PDFファイルの読み込みに失敗しました。ファイルが破損しているか、正しいPDF形式ではありません。'}), 400

        if not pages.strip():
            return jsonify({'error': '削除するページが指定されていません'}), 400

        reader = PdfReader(file)
        writer = PdfWriter()
        
        try:
            # 削除するページ番号を解析（例: "1,3,5-7"）
            pages_to_delete = set()
            for part in pages.split(','):
                part = part.strip()
                if not part:  # 空の部分をスキップ
                    continue
                if '-' in part:
                    start, end = map(int, part.split('-'))
                    if start < 1 or end > len(reader.pages) or start > end:
                        continue
                    pages_to_delete.update(range(start-1, end))
                else:
                    try:
                        page_num = int(part) - 1
                        if 0 <= page_num < len(reader.pages):
                            pages_to_delete.add(page_num)
                    except ValueError:
                        continue

            if not pages_to_delete:
                return jsonify({'error': '有効なページ番号が指定されていません'}), 400

            # 指定されたページ以外を追加
            for i in range(len(reader.pages)):
                if i not in pages_to_delete:
                    writer.add_page(reader.pages[i])

            if writer.pages:
                output = io.BytesIO()
                writer.write(output)
                output.seek(0)
                
                # 元のファイル名を基に新しいファイル名を生成
                original_name = os.path.splitext(file.filename)[0]
                new_filename = f'{original_name}_pages_deleted.pdf'
                
                return send_file(
                    output,
                    download_name=new_filename,
                    as_attachment=True,
                    mimetype='application/pdf'
                )
            else:
                return jsonify({'error': 'すべてのページが削除対象として指定されています'}), 400
                
        except ValueError:
            return jsonify({'error': '無効なページ番号が指定されました'}), 400
            
    except Exception as e:
        return jsonify({'error': f'ページ削除中にエラーが発生しました: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True) 