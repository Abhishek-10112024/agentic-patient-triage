from utils.validation import is_valid_input


def test_accepts_medical_symptom_input():
    assert is_valid_input("I have fever and body weakness")


def test_rejects_short_or_non_medical_input():
    assert not is_valid_input("ok")
    assert not is_valid_input("I want to book transport")


def test_rejects_common_asr_garbage():
    assert not is_valid_input("uh uh uh")
