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

    # 🚨 Rule 1: Red flag symptoms → force severe
    for keyword in RED_FLAG_KEYWORDS:
        if keyword in user_input_lower:
            llm_output["severity"] = "Severe"
            llm_output["response"] = (
                "⚠️ This may be a serious condition. Please seek immediate medical attention."
            )
            return llm_output

    # 🚨 Rule 2: Out-of-scope category → always severe
    if llm_output["category"] == "Other / Out-of-Scope":
        llm_output["severity"] = "Severe"

    return llm_output