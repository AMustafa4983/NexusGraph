from  pipeline import extraction_process
import requests
import json

from workers.organizer import Organizer
from flask import Flask, request, jsonify
import PyPDF2
import os


def extract_text_from_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfFileReader(file)
        text = ''
        for page_num in range(reader.numPages):
            text += reader.getPage(page_num).extractText()
    return text

def check_dataset(url):
    req = requests.get(url)
    content = json.loads(req.content)
    files = content['rows']

    return files

app = Flask(__name__)
organizer = Organizer('railway',
                'postgres',
                'ba**64B3f3*dd521Egef3g4*B-E-cA-3',
                'viaduct.proxy.rlwy.net',
                '36793')

@app.route('/api/papers', methods=['GET'])
def get_all_papers():
    papers = organizer.get_all_papers()
    return jsonify({'papers': papers}), 200

@app.route('/api/papers/<int:paper_id>', methods=['GET'])
def get_paper_details(paper_id):
    paper_details = organizer.get_paper_details(paper_id)
    return jsonify({'paper_details': paper_details}), 200

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        filename = file.filename
        file_path = os.path.join('uploads', filename)
        file.save(file_path)

        # Extract data from PDF or TXT
        if filename.endswith('.pdf'):
            text = extract_text_from_pdf(file_path)
        elif filename.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as txt_file:
                text = txt_file.read()
        else:
            return jsonify({'error': 'Unsupported file format'}), 400

        extraction_process(text)

        return jsonify({'message': 'File uploaded and data extracted successfully', 'text': text}), 200

@app.route('/api/process_external_data', methods=['POST'])
def process_external_data():
    data = request.json
    if 'url' not in data:
        return jsonify({'error': 'No URL provided in the request'}), 400

    url = data['url']
    response = requests.get(url)
    if response.status_code != 200:
        return jsonify({'error': 'Failed to retrieve data from the provided URL'}), 500

    content = json.loads(response.content)
    files = content.get('rows', [])

    for file in files:
        extraction_process(file)

    return jsonify({'message': 'Data extracted and processed successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True)