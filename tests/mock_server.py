from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

@app.route('/v1/agents/<agent_id>/interaction', methods=['POST'])
def botastico_mock(agent_id):

    data = request.get_json()
    if data is None:
        return jsonify({'error': 'Invalid request. Expected JSON data.'}), 400

    response = {
        "id": "mock_id",
        "object": "mock_object",
        "created_timestamp": datetime.now().isoformat(),
        "model": "mock_model",
        "usage": {},
        "finish_reason": "mock_finish_reason",
        "response_message": "Hello, I am the Botastico service!",
        "received_timestamp": datetime.now().isoformat(),
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(host='localhost', port=8000)