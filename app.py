from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
import os
import json

app = Flask(__name__)
CORS(app)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

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
    strategy = data.get("strategy", "conversion")

    general_rules = "\n".join(config["general_rules"])
    google_rules = "\n".join(config["google_ads_rules"])

    # 🔥 NEW: pull strict strategy rules from JSON
    strategy_rules_list = config.get("strategy_rules", {}).get(strategy, [])
    strategy_rules = "\n".join(strategy_rules_list)

    prompt = f"""
{config["system_prompt"]}

General Rules:
{general_rules}

Strategy Rules ({strategy}):
{strategy_rules}

Business: {business}
Goal: {goal}
Audience: {audience}

Google Ads Rules:
{google_rules}

Return ONLY valid JSON in this format:

{
  "offer": "string",
  "angles": ["string", "string", "string"],
  "facebook_ad": "string",
  "google_ads": {
    "headlines": ["string", "string", "string"],
    "descriptions": ["string", "string", "string"]
  },
  "ctas": ["string", "string"],
  "email": {
    "subject": "string",
    "body": "string"
  }
}
"""

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6,
        max_completion_tokens=1200
    )

    raw = completion.choices[0].message.content.strip()

    start = raw.find("{")
    end = raw.rfind("}")

    if start == -1 or end == -1:
        return jsonify({"error": "No JSON returned", "raw": raw}), 500

    try:
        return jsonify(json.loads(raw[start:end+1]))
    except Exception as e:
        return jsonify({"error": str(e), "raw": raw}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 1000))
    app.run(host="0.0.0.0", port=port)
