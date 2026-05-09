from flask import Flask, render_template, request
import pytesseract
from PIL import Image
import easyocr
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Upload folder
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create uploads folder automatically
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# EasyOCR
reader = easyocr.Reader(['en'])

@app.route('/', methods=['GET', 'POST'])
def index():

    extracted_text = ""

    if request.method == 'POST':

        # Check file exists
        if 'image' not in request.files:
            return render_template(
                'index.html',
                text="No image uploaded"
            )

        file = request.files['image']

        # No file selected
        if file.filename == '':
            return render_template(
                'index.html',
                text="Please select an image"
            )

        # OCR mode
        mode = request.form.get('mode')

        # Secure filename
        filename = secure_filename(file.filename)

        # Full file path
        filepath = os.path.join(
            app.config['UPLOAD_FOLDER'],
            filename
        )

        # Save uploaded image dynamically
        file.save(filepath)

        try:

            # Printed OCR
            if mode == 'printed':

                extracted_text = pytesseract.image_to_string(
                    Image.open(filepath)
                )

            # Handwritten OCR
            elif mode == 'handwritten':

                extracted_text = pytesseract.image_to_string(
                    Image.open(filepath),
                    config='--psm 6'
                )

            # Deep Learning OCR
            elif mode == 'easyocr':

                result = reader.readtext(
                    filepath,
                    detail=0
                )

                extracted_text = " ".join(result)

            else:

                extracted_text = "Invalid OCR Mode"

        except Exception as e:

            extracted_text = f"Error: {str(e)}"

    return render_template(
        'index.html',
        text=extracted_text
    )

if __name__ == '__main__':
    app.run(debug=True)