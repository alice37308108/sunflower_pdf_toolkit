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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'ファイルがありません'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'ファイルが選択されていません'}), 400
    
    if file and file.filename.endswith('.pdf'):
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
    
    return jsonify({'error': 'PDFファイルのみ対応しています'}), 400

@app.route('/extract-text', methods=['POST'])
def extract_text():
    if 'file' not in request.files:
        return jsonify({'error': 'ファイルがありません'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'ファイルが選択されていません'}), 400

    if file and file.filename.endswith('.pdf'):
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n\n"
        return jsonify({'text': text})

    return jsonify({'error': 'PDFファイルのみ対応しています'}), 400

@app.route('/merge-pdfs', methods=['POST'])
def merge_pdfs():
    if 'files[]' not in request.files:
        return jsonify({'error': 'ファイルがありません'}), 400

    files = request.files.getlist('files[]')
    if not files or files[0].filename == '':
        return jsonify({'error': 'ファイルが選択されていません'}), 400

    merger = PdfMerger()
    
    for file in files:
        if file.filename.endswith('.pdf'):
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

@app.route('/split-pdf', methods=['POST'])
def split_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'ファイルがありません'}), 400

    file = request.files['file']
    page_ranges = request.form.get('pages', '').split(',')
    
    if file.filename == '' or not page_ranges:
        return jsonify({'error': 'ファイルまたはページ範囲が指定されていません'}), 400

    if file and file.filename.endswith('.pdf'):
        reader = PdfReader(file)
        writer = PdfWriter()
        
        for page_range in page_ranges:
            try:
                if '-' in page_range:
                    start, end = map(int, page_range.split('-'))
                    for i in range(start-1, min(end, len(reader.pages))):
                        writer.add_page(reader.pages[i])
                else:
                    page_num = int(page_range) - 1
                    if 0 <= page_num < len(reader.pages):
                        writer.add_page(reader.pages[page_num])
            except ValueError:
                continue
        
        output = io.BytesIO()
        writer.write(output)
        output.seek(0)
        
        return send_file(
            output,
            download_name='split.pdf',
            as_attachment=True,
            mimetype='application/pdf'
        )

    return jsonify({'error': 'PDFファイルのみ対応しています'}), 400

@app.route('/rotate-pdf', methods=['POST'])
def rotate_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'ファイルがありません'}), 400

    file = request.files['file']
    rotation = int(request.form.get('rotation', 90))
    
    if file.filename == '':
        return jsonify({'error': 'ファイルが選択されていません'}), 400

    if file and file.filename.endswith('.pdf'):
        reader = PdfReader(file)
        writer = PdfWriter()
        
        for page in reader.pages:
            page.rotate(rotation)
            writer.add_page(page)
        
        output = io.BytesIO()
        writer.write(output)
        output.seek(0)
        
        return send_file(
            output,
            download_name='rotated.pdf',
            as_attachment=True,
            mimetype='application/pdf'
        )

    return jsonify({'error': 'PDFファイルのみ対応しています'}), 400

@app.route('/add-watermark', methods=['POST'])
def add_watermark():
    if 'file' not in request.files or 'watermark' not in request.files:
        return jsonify({'error': 'メインファイルまたは透かしファイルがありません'}), 400

    file = request.files['file']
    watermark = request.files['watermark']
    
    if file.filename == '' or watermark.filename == '':
        return jsonify({'error': 'ファイルが選択されていません'}), 400

    if file.filename.endswith('.pdf') and watermark.filename.endswith('.pdf'):
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

    return jsonify({'error': 'PDFファイルのみ対応しています'}), 400

if __name__ == '__main__':
    app.run(debug=True) 