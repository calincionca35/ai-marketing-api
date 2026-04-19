from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
import os
import json

app = Flask(__name__)
CORS(app)

# Groq client (API key stored in Render/GitHub env vars)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()

    business = data.get("business", "")
    goal = data.get("goal", "")
    audience = data.get("audience", "")

    prompt = f"""
Return ONLY valid JSON.

Create a marketing campaign.

Business: {business}
Goal: {goal}
Audience: {audience}

Format exactly like this:

{{
  "offer": "",
  "angles": [],
  "facebook_ad": "",
  "google_ads": {{
    "headlines": [],
    "descriptions": []
  }},
  "ctas": [],
  "email": {{
    "subject": "",
    "body": ""
  }}
}}
"""

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_completion_tokens=1500
    )

    response_text = completion.choices[0].message.content

    # Convert AI text → real JSON
    try:
        response_json = json.loads(response_text)
    except Exception:
        return jsonify({
            "error": "Invalid JSON returned from model",
            "raw": response_text
        }), 500

    return jsonify(response_json)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 1000))
    app.run(host="0.0.0.0", port=port)
