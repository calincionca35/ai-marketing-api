from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
import os
import json

app = Flask(__name__)
CORS(app)

# Groq client (requires GROQ_API_KEY in Render env vars)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()

    business = data.get("business", "")
    goal = data.get("goal", "")
    audience = data.get("audience", "")

    prompt = f"""
You are a strict JSON generator.

Rules:
- Output ONLY valid JSON
- Do NOT use markdown or backticks
- Do NOT leave empty fields
- Every field must contain useful marketing content

Business: {business}
Goal: {goal}
Audience: {audience}

Return EXACTLY this structure:

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

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_completion_tokens=1500
        )

        response_text = completion.choices[0].message.content.strip()

        # Try direct JSON parse
        try:
            return jsonify(json.loads(response_text))

        except Exception:
            # fallback: extract JSON block
            start = response_text.find("{")
            end = response_text.rfind("}")

            if start != -1 and end != -1:
                cleaned = response_text[start:end+1]
                return jsonify(json.loads(cleaned))

            return jsonify({
                "error": "Model did not return valid JSON",
                "raw": response_text
            }), 500

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 1000))
    app.run(host="0.0.0.0", port=port)
