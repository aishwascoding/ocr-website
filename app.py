from flask import Flask, render_template, request, Response
from PIL import Image
import pytesseract
import os
import uuid

# ✅ Tell Pytesseract where to find Tesseract on Railway
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return "No file part"

    file = request.files['file']
    if file.filename == '':
        return "No selected file"

    lang = request.form.get('lang', 'eng')  # Default to English

    try:
        input_img = Image.open(file.stream).convert("RGB")
    except Exception as e:
        return f"Error opening image: {e}"

    safe_filename = f"{uuid.uuid4()}.jpg"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)

    input_img.save(filepath, "JPEG")

    try:
        text = pytesseract.image_to_string(input_img, lang=lang)
    except Exception as e:
        return f"OCR Error: {e}"

    clean_text = text.strip() or "No text found."

    return render_template('result.html',
                           extracted_text=clean_text,
                           image_path=safe_filename)

@app.route('/download-text')
def download_text():
    text = request.args.get('text', 'No text found.')
    return Response(text, mimetype='text/plain',
                    headers={'Content-Disposition': 'attachment;filename=extracted_text.txt'})

if __name__ == '__main__':
    app.run()