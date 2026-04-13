from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()

    business = data.get("business", "")
    goal = data.get("goal", "")
    audience = data.get("audience", "")

    return jsonify({
    "offer": "For busy professionals, get premium coffee in under 2 minutes without waiting in line.",

    "angles": [
        "Speed: No waiting",
        "Convenience: Order ahead",
        "Productivity: Save time every morning",
        "Quality: Premium taste fast",
        "Stress-free mornings"
    ],

    "facebook_ad": "Still waiting in line for coffee? Get premium coffee in under 2 minutes and take back your mornings.",

    "google_ads": {
        "headlines": [
            "Fast Coffee in 2 Minutes",
            "Skip the Coffee Line",
            "Order Ahead Coffee"
        ],
        "descriptions": [
            "Premium coffee, no waiting.",
            "Order ahead and grab instantly."
        ]
    },

    "ctas": [
        "Order Ahead Now",
        "Skip the Line",
        "Get Coffee Fast"
    ],

    "email": {
        "subject": "Your coffee is ready before you arrive",
        "body": "Order ahead and get premium coffee in under 2 minutes. No more waiting in line."
    }
})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
