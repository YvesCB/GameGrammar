from pprint import pprint
import textwrap
import crayons


def get_unicode_digit(number):
    digits = ['⓪', '①', '②', '③', '④', '⑤', '⑥', '⑦', '⑧', '⑨', '⑩']
    if number < len(digits):
        return digits[number]
    else:
        return f'({number})'


def log_header(text):
    print()
    print(crayons.green('- ' + str(text)))


def log_section(text):
    print()
    print(crayons.green('-- ' + str(text)))


def log_subsection(text):
    print()
    print(crayons.green(str(text)))


def log_body(text):
    print(textwrap.fill(text, 100))


def log_kv(key, value=None, oneline=False, nopprint=False):
    if value is None:
        print(crayons.blue(str(key)))
    else:
        if len(str(value)) > 50 and not oneline:
            print(crayons.blue(str(key)))
            if nopprint:
                print(value)
            else:
                pprint(value)
        else:
            print(crayons.blue(str(key)) + '\t' + str(value))
