import json
import os
from flask import Flask, request, jsonify, render_template, send_from_directory, redirect, url_for, session
from flask_cors import CORS
from pdf_extractor import extract_text_from_pdf, summarize_relevant_information
from llm import start_sales_conversation, get_ai_response
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default_secret_key')

UPLOAD_FOLDER = 'UPLOADS'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

JSON_FILE_PATH = os.path.join(UPLOAD_FOLDER, 'product_data.json')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico')

@app.route('/get-deepgram-key', methods=['GET'])
def get_deepgram_key():
    DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY')
    if not DEEPGRAM_API_KEY:
        print("Error: Deepgram API key not found")  # Log error using print
        return jsonify({'error': 'Deepgram API key not found'}), 500
    return jsonify({'deepgram_api_key': DEEPGRAM_API_KEY})

@app.route('/save', methods=['POST'])
def handle_product():
    try:
        company_name = request.form.get('companyName')
        product_name = request.form.get('productName')
        product_description = request.form.get('productDescription')
        pdf_file = request.files.get('pdfUpload')

        if not company_name or not product_name:
            print("Error: Company Name and Product Name are required!")  # Log error using print
            return jsonify({'message': 'Company Name and Product Name are required!'}), 400

        pdf_text = ''
        if pdf_file and pdf_file.filename.endswith('.pdf'):
            pdf_filename = "product.pdf"
            pdf_path = os.path.join(UPLOAD_FOLDER, pdf_filename)
            pdf_file.save(pdf_path)
            try:
                pdf_text = extract_text_from_pdf(pdf_path)
                print("PDF Summary:", summarize_relevant_information(pdf_path))  # Log summary using print
            except Exception as e:
                print(f"Error: Failed to extract text from PDF - {str(e)}")  # Log error using print
                return jsonify({'message': 'Failed to process PDF file'}), 500

        product_data = {
            'companyName': company_name,
            'productName': product_name,
            'productDescription': product_description,
            'pdfText': pdf_text
        }

        with open(JSON_FILE_PATH, 'w') as json_file:
            json.dump(product_data, json_file, indent=4)

        print("Product data saved successfully")  # Log success using print
        return redirect(url_for('talk'))

    except Exception as e:
        print(f"Error: An error occurred - {str(e)}")  # Log error using print
        return jsonify({'message': f'An error occurred: {str(e)}'}), 500

@app.route('/start', methods=['GET'])
def start_conversation():
    session['conversation_history'] = start_sales_conversation()
    ai_message = "Hello! My name is Pooja. May I have your first and last name, please?"
    print("Conversation started")  # Log using print
    return jsonify({'status': 'success', 'message': 'Transcript received', 'response': ai_message})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/talk')
def talk():
    return render_template('talk.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/product')
def product():
    return render_template('product.html')

@app.route('/transcript', methods=['POST'])
def receive_transcript():
    data = request.get_json()
    transcript = data.get('transcript', '')
    
    if not transcript:
        print("Error: Empty transcript received")  # Log error using print
        return jsonify({'status': 'error', 'message': 'Empty transcript'}), 400
    
    conversation_history = session.get('conversation_history', [])
    ai_response, updated_history = get_ai_response(transcript, conversation_history)
    session['conversation_history'] = updated_history
    
    if not ai_response:
        print("Error: Failed to get OpenAI response")  # Log error using print
        return jsonify({'status': 'error', 'message': 'Failed to get OpenAI response'}), 500
    
    return jsonify({'status': 'success', 'message': 'Transcript received', 'response': ai_response})

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    print(f"Starting Flask app on port {port}")  # Log app start using print
    app.run(host='0.0.0.0', port=port)