from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
import os
import json
import re

app = Flask(__name__)
CORS(app)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


def load_prompt_config():
    with open("prompt_config.json", "r") as f:
        return json.load(f)


config = load_prompt_config()


def extract_json(raw):
    """
    Safely extract JSON from model output.
    Prevents 500 crashes from bad formatting.
    """
    try:
        return json.loads(raw)
    except:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except:
                return None
        return None


@app.route("/generate", methods=["POST"])
def generate():
    try:
        data = request.get_json() or {}

        business = data.get("business", "")
        goal = data.get("goal", "")
        audience = data.get("audience", "")
        strategy = data.get("strategy", "conversion")

        general_rules = "\n".join(config["general_rules"])
        google_rules = "\n".join(config["google_ads_rules"])

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
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_completion_tokens=1200
        )

        raw = completion.choices[0].message.content.strip()

        parsed = extract_json(raw)

        if not parsed:
            return jsonify({
                "error": "Invalid JSON from model",
                "raw": raw
            }), 500

        return jsonify(parsed)

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 1000))
    app.run(host="0.0.0.0", port=port)
