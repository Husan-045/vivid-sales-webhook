from app.service.example import Example


def test_example():
    assert Example().hello_world("test")=="hello test"
