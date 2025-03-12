from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/errors', methods=['POST'])
def receive_errors():
    data = request.json  # Get JSON data from request
    if not data:
        return jsonify({"status": "error", "message": "No data received"}), 400

    # Print received error
    print(f"Received Error: {data}")

    return jsonify({"status": "success", "message": "Error logged successfully"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
