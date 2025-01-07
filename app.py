from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')


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
