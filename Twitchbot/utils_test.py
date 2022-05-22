from utils import get_unicode_digit

digits = ['⓪', '①', '②', '③', '④', '⑤', '⑥', '⑦', '⑧', '⑨', '⑩']

def test_get_unicode_digit():
    for number in range(len(digits)):
        assert get_unicode_digit(number) == digits[number]
