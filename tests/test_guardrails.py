from services.guardrails import apply_guardrails


def test_red_flag_symptom_forces_severe_with_summary():
    llm_output = {
        "category": "Upper Respiratory Issue",
        "severity": "Mild",
        "response": "Rest and drink fluids.",
        "summary": None,
    }

    result = apply_guardrails("I have chest pain and difficulty breathing", llm_output)

    assert result["severity"] == "Severe"
    assert result["category"] == "Other / Out-of-Scope"
    assert "immediate medical attention" in result["response"].lower()
    assert result["summary"]["recommendation"] == "Immediate medical attention required"


def test_out_of_scope_never_returns_home_remedies():
    llm_output = {
        "category": "Other / Out-of-Scope",
        "severity": "Mild",
        "response": "Try a home remedy.",
        "summary": None,
    }

    result = apply_guardrails("I have ankle pain", llm_output)

    assert result["severity"] == "Severe"
    assert "consult a doctor" in result["response"].lower()
