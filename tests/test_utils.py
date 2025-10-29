from madr.utils import sanitize_string


def test_sanitize_string():
    assert sanitize_string("  João da Silva  ") == "joão da silva"
    assert sanitize_string("Maria   de   Souza") == "maria de souza"
    assert sanitize_string("  Ana-Maria  ") == "anamaria"
    assert not sanitize_string("   ")
    assert not sanitize_string("")
    assert sanitize_string(None) is None
