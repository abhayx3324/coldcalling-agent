import json
import os
from flask import Flask, request, jsonify, render_template, redirect
from flask_cors import CORS  # Import CORS
from flask_socketio import SocketIO
from pdf_extractor import extract_text_from_pdf, summarize_relevant_information
from llm import start_sales_conversation, get_ai_response

app = Flask(__name__)
CORS(app)  # Enable CORS globally for all routes
socketio = SocketIO(app, cors_allowed_origins="*")

UPLOAD_FOLDER = 'UPLOADS'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

JSON_FILE_PATH = 'product_data.json'

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
def start_conversation():
    global conversation_history
    conversation_history = start_sales_conversation()
    
    ai_message = "Hello! My name is Ravi. May I have your first and last name, please?"
    
    return jsonify({'status': 'success', 'message': 'Transcript received', 'response': ai_message})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/product')
def company():
    return render_template('company.html')

@app.route('/transcript', methods=['POST'])
def receive_transcript():
    global conversation_history
    
    data = request.get_json()
    
    print(f"{data}")
    transcript = data.get('transcript', '')
    
    if not transcript:
        return jsonify({'status': 'error', 'message': 'Empty transcript'}), 400
    
    ai_response, conversation_history = get_ai_response(transcript, conversation_history)
    
    if not ai_response:
        return jsonify({'status': 'error', 'message': 'Failed to get OpenAI response'}), 500
    
    return jsonify({'status': 'success', 'message': 'Transcript received', 'response': ai_response})

if __name__ == '__main__':
    app.run(debug=True)