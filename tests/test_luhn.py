from app.utils.luhn import validate_luhn


def test_valid_luhn():
    # classic test number
    assert validate_luhn("79927398713") is True


def test_invalid_luhn():
    assert validate_luhn("79927398710") is False
