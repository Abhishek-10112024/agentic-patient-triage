def is_valid_input(text: str):
    if not text or len(text.strip()) < 5:
        return False

    # Common ASR garbage patterns
    garbage_patterns = [
        "i see one",
        "and i for",
        "uh",
        "hmm"
    ]

    text_lower = text.lower()

    for pattern in garbage_patterns:
        if pattern in text_lower:
            return False

    return True