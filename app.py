from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
import os
import json

app = Flask(__name__)
CORS(app)

# Load Groq API key
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Load prompt config from JSON file
def load_prompt_config():
    with open("prompt_config.json", "r") as f:
        return json.load(f)

config = load_prompt_config()


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json() or {}

    business = data.get("business", "")
    goal = data.get("goal", "")
    audience = data.get("audience", "")

    prompt = f"""
{config["system_prompt"]}

Rules:
{chr(10).join(config["rules"])}

Return ONLY valid JSON.

Business: {business}
Goal: {goal}
Audience: {audience}

Return in this format:

{{
  "offer": "string",
  "angles": ["string", "string", "string"],
  "facebook_ad": "string",
  "google_ads": {{
    "headlines": ["string", "string", "string"],
    "descriptions": ["string", "string", "string"]
  }},
  "ctas": ["string", "string"],
  "email": {{
    "subject": "string",
    "body": "string"
  }}
}}
"""

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_completion_tokens=1200
    )

    response_text = completion.choices[0].message.content.strip()

    # Extract JSON safely
    start = response_text.find("{")
    end = response_text.rfind("}")

    if start == -1 or end == -1:
        return jsonify({
            "error": "No JSON returned",
            "raw": response_text
        }), 500

    try:
        data = json.loads(response_text[start:end+1])
        return jsonify(data)
    except Exception as e:
        return jsonify({
            "error": str(e),
            "raw": response_text
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 1000))
    app.run(host="0.0.0.0", port=port)
