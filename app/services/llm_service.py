import os
from groq import Groq
from dotenv import load_dotenv
import json
from models.triage_schema import TriageResponse
from services.guardrails import apply_guardrails

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


SYSTEM_PROMPT = """
You are a medical triage assistant for rural patients.

Your job:
1. Understand patient symptoms
2. Classify into ONE category:
   - Upper Respiratory Issue
   - Fever-Related Condition
   - Other / Out-of-Scope

3. Assess severity:
   - Mild
   - Severe

4. Respond STRICTLY in JSON format:

{
  "category": "...",
  "severity": "...",
  "response": "...",
  "summary": {
    "symptoms": "...",
    "duration": "...",
    "severity_reason": "...",
    "recommendation": "..."
  }
}

Rules:
- Be safe and conservative → if unsure, mark as Severe
- Mild → give simple home remedies
- Severe → DO NOT give treatment → recommend doctor
- "summary" MUST be filled ONLY for severe cases, else null
- Keep response empathetic and simple
"""


def analyze_patient(text: str):
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            temperature=0.2,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ],
        )

        raw_output = completion.choices[0].message.content

        # 🔒 Step 1: Convert string → JSON
        parsed_output = json.loads(raw_output)

        # 🔒 Step 2: Validate using Pydantic
        validated_output = TriageResponse(**parsed_output)

        # 🔒 Step 3: Apply guardrails
        final_output = apply_guardrails(text, validated_output.dict())

        return final_output

    except Exception as e:
        return {
            "error": str(e),
            "raw_output": raw_output if 'raw_output' in locals() else None
        }