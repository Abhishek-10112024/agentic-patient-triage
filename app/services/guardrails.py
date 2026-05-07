RED_FLAG_KEYWORDS = [
    "chest pain",
    "difficulty breathing",
    "shortness of breath",
    "unconscious",
    "seizure",
    "severe bleeding",
    "high fever for more than 3 days",
    "vomiting blood",
    "black stool",
    "severe headache",
    "blurred vision"
]


def apply_guardrails(user_input: str, llm_output: dict):
    user_input_lower = user_input.lower()

    # 🚨 Rule 1: Red flag symptoms → force Severe (assignment: emergency)
    for keyword in RED_FLAG_KEYWORDS:
        if keyword in user_input_lower:
            llm_output["severity"] = "Severe"
            llm_output["category"] = "Other / Out-of-Scope"
            llm_output["response"] = (
                "⚠️ This may be a serious condition. Please seek immediate medical attention immediately."
            )

            # Ensure summary exists
            if not llm_output.get("summary"):
                llm_output["summary"] = {
                    "symptoms": user_input,
                    "duration": "Not specified",
                    "severity_reason": "Presence of emergency red flag symptoms",
                    "recommendation": "Immediate medical attention required"
                }

            return llm_output

    # 🚨 Rule 2: Other category → ALWAYS severe (assignment rule)
    if llm_output["category"] == "Other / Out-of-Scope":
        llm_output["severity"] = "Severe"

        # Ensure no home remedies leak
        llm_output["response"] = (
            "⚠️ Your symptoms require medical attention. Please consult a doctor."
        )

    return llm_output