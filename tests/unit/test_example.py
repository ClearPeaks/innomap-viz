from src.example import my_sum


def test_sum() -> None:
    assert my_sum(3, 2) == 5
