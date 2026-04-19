from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
import os
import json

app = Flask(__name__)
CORS(app)

# Groq client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Load prompt config
def load_prompt_config():
    with open("prompt_config.json", "r") as f:
        return json.load(f)

config = load_prompt_config()


# ---------- ENFORCE GOOGLE ADS LIMITS ----------
def enforce_limits(data):
    if "google_ads" in data:
        if "headlines" in data["google_ads"]:
            data["google_ads"]["headlines"] = [
                h[:30] for h in data["google_ads"]["headlines"]
            ]

        if "descriptions" in data["google_ads"]:
            data["google_ads"]["descriptions"] = [
                d[:90] for d in data["google_ads"]["descriptions"]
            ]

    return data


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

Return EXACT format:

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

        # enforce Google Ads limits here
        data = enforce_limits(data)

        return jsonify(data)

    except Exception as e:
        return jsonify({
            "error": str(e),
            "raw": response_text
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 1000))
    app.run(host="0.0.0.0", port=port)
