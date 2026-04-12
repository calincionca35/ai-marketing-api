from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()

    business = data.get("business", "")
    goal = data.get("goal", "")
    audience = data.get("audience", "")

    return jsonify({
        "business": business,
        "goal": goal,
        "audience": audience,
        "campaign": {
            "idea": f"Run a {goal} campaign for {business} targeting {audience}",
            "steps": [
                "Define core message",
                "Create 3 social posts",
                "Send one email blast"
            ],
            "cta": "Start today with a simple landing page"
        }
    })

if __name__ == "__main__":
    app.run()
