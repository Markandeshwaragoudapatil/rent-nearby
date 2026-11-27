from app.security import hash_password, verify_password

def test_password_hash_is_not_plain_text():
    encoded = hash_password("correct horse battery staple")
    assert encoded != "correct horse battery staple"
    assert verify_password(encoded, "correct horse battery staple")

def test_wrong_password_does_not_verify():
    encoded = hash_password("correct horse battery staple")
    assert not verify_password(encoded, "wrong password")
