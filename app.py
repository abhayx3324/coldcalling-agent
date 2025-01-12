#app.py
import json

import os

from flask import Flask, flash, request, jsonify, render_template, redirect
from flask_cors import CORS, cross_origin
from flask_socketio import SocketIO

from pdf_extractor import extract_text_from_pdf, summarize_relevant_information
from llm import start_sales_conversation, get_ai_response
from cartesia_tts import speak

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

UPLOAD_FOLDER = 'UPLOADS'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

JSON_FILE_PATH = 'product_data.json'

def genHeader(sampleRate, bitsPerSample, channels):
    datasize = 2000*10**6
    o = bytes("RIFF",'ascii')                                               # (4byte) Marks file as RIFF
    o += (datasize + 36).to_bytes(4,'little')                               # (4byte) File size in bytes excluding this and RIFF marker
    o += bytes("WAVE",'ascii')                                              # (4byte) File type
    o += bytes("fmt ",'ascii')                                              # (4byte) Format Chunk Marker
    o += (16).to_bytes(4,'little')                                          # (4byte) Length of above format data
    o += (1).to_bytes(2,'little')                                           # (2byte) Format type (1 - PCM)
    o += (channels).to_bytes(2,'little')                                    # (2byte)
    o += (sampleRate).to_bytes(4,'little')                                  # (4byte)
    o += (sampleRate * channels * bitsPerSample // 8).to_bytes(4,'little')  # (4byte)
    o += (channels * bitsPerSample // 8).to_bytes(2,'little')               # (2byte)
    o += (bitsPerSample).to_bytes(2,'little')                               # (2byte)
    o += bytes("data",'ascii')                                              # (4byte) Data Chunk Marker
    o += (datasize).to_bytes(4,'little')                                    # (4byte) Data size in bytes
    return o

@app.route('/save', methods=['POST'])
def handle_product():
    company_name = request.form.get('companyName')
    product_name = request.form.get('productName')
    product_description = request.form.get('productDescription')

    pdf_file = request.files.get('pdfUpload')

    if pdf_file:
        pdf_filename = "product.pdf"
        pdf_path = os.path.join(UPLOAD_FOLDER, pdf_filename)
        pdf_file.save(pdf_path)

        pdf_text = extract_text_from_pdf(pdf_path)
        
        print(summarize_relevant_information(pdf_path))
        
    else:
        pdf_text = ''

    product_data = {
        'companyName': company_name,
        'productName': product_name,
        'productDescription': product_description,
        'pdfText': pdf_text  # Store the path to the uploaded PDF
    }

    with open(JSON_FILE_PATH, 'w') as json_file:
            json.dump(product_data, json_file, indent=4)

    return jsonify({'message': 'Product information saved successfully!', 'productData': product_data}), 200

@app.route('/start', methods=['GET'])
@cross_origin()
def start_conversation():
    global conversation_history
    conversation_history = start_sales_conversation()
    
    ai_message = "Hello! My name is Ravi. May I have your first and last name, please?"
    speak(ai_message)  # Assuming you have a function that makes the AI speak
    return jsonify({"message": ai_message})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/product')
def company():
    return render_template('company.html')


@app.route('/transcript', methods=['POST'])
@cross_origin()
def receive_transcript():
    global conversation_history
    
    data = request.get_json()
    
    print(f"{data}")
    transcript = data.get('transcript', '')
    
    if not transcript:
        return jsonify({'status': 'error', 'message': 'Empty transcript'}), 400
    
    ai_reply, conversation_history = get_ai_response(transcript, conversation_history)
    
    speak(ai_reply)
    
    print()
    
    print(f"Received transcript: {transcript}")
    return jsonify({'status': 'success', 'message': 'Transcript received'})

if __name__ == '__main__':
    app.run(debug=True)