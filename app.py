from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
import os
import json

app = Flask(__name__)
CORS(app)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json() or {}

    business = data.get("business", "")
    goal = data.get("goal", "")
    audience = data.get("audience", "")

    prompt = f"""
Return ONLY valid JSON.

Do not return empty values.

Business: {business}
Goal: {goal}
Audience: {audience}

Return:

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
        temperature=0.8,
        max_completion_tokens=1200
    )

    raw = completion.choices[0].message.content.strip()

    print("RAW:", raw)

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
