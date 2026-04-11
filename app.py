from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    goal = data.get("goal", "")

    return jsonify({
        "result": "Marketing idea for: " + goal
    })

if __name__ == "__main__":
    app.run()
