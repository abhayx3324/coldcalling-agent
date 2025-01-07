import json
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def save_product_data(company_name, product_name, product_description):
    product_data = {
        'company_name': company_name,
        'product_name': product_name,
        'product_description': product_description
    }

    # Write the new product data to the file (overwrite existing data)
    with open('product_data.json', 'w') as file:
        json.dump(product_data, file, indent=4)

@app.route('/product', methods=['POST'])
def receive_product_info():
    data = request.get_json()
    company_name = data.get('companyName', '')
    product_name = data.get('productName', '')
    product_description = data.get('productDescription', '')

    # Save the product data to a JSON file
    save_product_data(company_name, product_name, product_description)

    # Print the received data
    print(f"Company Name: {company_name}")
    print(f"Product Name: {product_name}")
    print(f"Product Description: {product_description}")

    # Respond back with success
    return jsonify({'status': 'success', 'message': 'Product information received'})

    # Respond back with success
    return jsonify({'status': 'success', 'message': 'Product information received'})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/company')
def company():
    return render_template('company.html')


@app.route('/transcript', methods=['POST'])
def receive_transcript():
    str = ''
    data = request.get_json()
    transcript = data.get('transcript', '')
    str += transcript
    
    print(f"Received transcript: {str}")
    return jsonify({'status': 'success', 'message': 'Transcript received'})

if __name__ == '__main__':
    app.run(debug=True)
