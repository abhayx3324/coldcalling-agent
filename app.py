import json
import os
from flask import Flask, request, jsonify, render_template, send_from_directory, redirect, url_for, session
from flask_cors import CORS, cross_origin
from pdf_extractor import extract_text_from_pdf, summarize_relevant_information
from llm import start_sales_conversation, get_ai_response
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
# Set a secret key for the Flask session
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default_secret_key')

# Define allowed origins for Cross-Origin Resource Sharing (CORS)
allowed_origins = ["http://localhost:5000", "http://127.0.0.1:5000", "http://127.0.0.1:8080"]
# Add more origins as needed

# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": allowed_origins}})

# Define upload folder for storing uploaded files
UPLOAD_FOLDER = 'UPLOADS'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Path for storing product data as a JSON file
JSON_FILE_PATH = 'product_data.json'

# Route to serve the favicon
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder, 'favicon.ico')

# Route to retrieve the Deepgram API key
@app.route('/get-deepgram-key', methods=['GET'])
def get_deepgram_key():
    DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY')
    if not DEEPGRAM_API_KEY:
        return jsonify({'error': 'Deepgram API key not found'}), 500
    return jsonify({'deepgram_api_key': DEEPGRAM_API_KEY})

# Route to handle saving product data
@app.route('/save', methods=['POST'])
def handle_product():
    try:
        # Retrieve form data
        company_name = request.form.get('companyName')
        product_name = request.form.get('productName')
        product_description = request.form.get('productDescription')
        pdf_file = request.files.get('pdfUpload')

        # Validate required fields
        if not company_name or not product_name:
            return jsonify({'message': 'Company Name and Product Name are required!'}), 400

        # Handle PDF upload if provided
        pdf_text = ''
        if pdf_file:
            # Save uploaded PDF file
            pdf_filename = "product.pdf"
            pdf_path = os.path.join(UPLOAD_FOLDER, pdf_filename)
            pdf_file.save(pdf_path)
            # Extract and summarize text from the PDF
            pdf_text = extract_text_from_pdf(pdf_path)
            print(summarize_relevant_information(pdf_path))

        # Prepare product data for saving
        product_data = {
            'companyName': company_name,
            'productName': product_name,
            'productDescription': product_description,
            'pdfText': pdf_text
        }

        # Save product data to a JSON file
        with open(JSON_FILE_PATH, 'w') as json_file:
            json.dump(product_data, json_file, indent=4)

        # Redirect to the talk page if successful
        return redirect(url_for('talk'))

    except Exception as e:
        # Handle errors gracefully
        return jsonify({'message': f'An error occurred: {str(e)}'}), 500

# Route to start a conversation
@app.route('/start', methods=['GET'])
def start_conversation():
    global conversation_history
    # Initialize a new sales conversation
    conversation_history = start_sales_conversation()
    
    # Initial AI message
    ai_message = "Hello! My name is Pooja. May I have your first and last name, please?"
    
    return jsonify({'status': 'success', 'message': 'Transcript received', 'response': ai_message})

# Route to serve the home page
@app.route('/')
def index():
    return render_template('index.html')

# Route to serve the talk page
@app.route('/talk')
def talk():
    return render_template('talk.html')

# Route to serve the about page
@app.route('/about')
def about():
    return render_template('about.html')

# Route to serve the product page
@app.route('/product')
def product():
    return render_template('product.html')

# Route to receive a transcript and generate AI responses
@app.route('/transcript', methods=['POST'])
def receive_transcript():
    global conversation_history
    
    # Parse incoming JSON data
    data = request.get_json()
    
    print(f"{data}")
    transcript = data.get('transcript', '')
    
    # Validate the transcript
    if not transcript:
        return jsonify({'status': 'error', 'message': 'Empty transcript'}), 400
    
    # Get AI response and update conversation history
    ai_response, conversation_history = get_ai_response(transcript, conversation_history)
    
    # Handle cases where AI response generation fails
    if not ai_response:
        return jsonify({'status': 'error', 'message': 'Failed to get OpenAI response'}), 500
    
    # Return the AI response
    return jsonify({'status': 'success', 'message': 'Transcript received', 'response': ai_response})

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
