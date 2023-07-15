from flask import Flask, request, jsonify
from datetime import datetime
import time

app = Flask(__name__)

@app.route('/v1/agents/<agent_id>/interactions', methods=['POST'])
def botastico_mock(agent_id):

    data = request.get_json()
    if data is None:
        return jsonify({'error': 'Invalid request. Expected JSON data.'}), 400

    timestamp = int(time.mktime(datetime.now().timetuple()))

    response = {
        "id": "chatcmpl-mockId",
        "object": "chat.completion",
        "created": timestamp,
        "model": "gpt-4-0613",
        "choices": [
            {
                "index": 0, 
                "message": {
                    "role": "assistant", 
                    "content": "Hello, I am the Botastico service!"
                }, 
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 63,
            "completion_tokens": 9,
            "total_tokens": 72
        }
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(host='localhost', port=8000)