def is_valid_input(text: str):
    if not text:
        return False

    text = text.strip().lower()

    # 🚨 Too short
    if len(text) < 6:
        return False

    # 🚨 Repeated meaningless words
    words = text.split()
    if len(set(words)) <= 2:
        return False

    # 🚨 Common ASR garbage patterns
    garbage_patterns = [
        "i see one",
        "and i for",
        "uh",
        "hmm",
        "ah",
        "noise"
    ]

    for pattern in garbage_patterns:
        if pattern in text:
            return False

    # 🚨 Medical keyword check (important)
    medical_keywords = [
        "fever", "pain", "cough", "cold", "headache",
        "breathing", "vomit", "nausea", "chest",
        "throat", "body", "weakness"
    ]

    if not any(word in text for word in medical_keywords):
        return False

    return True