'''enum conversion tests'''
from enum import Enum
from rune.runtime.utils import rune_str


def test_simple_conv():
    '''test simple conversions'''
    assert "1" == rune_str(1)
    assert "9.5" == rune_str(9.5)
    assert "abcdef" == rune_str("abcdef")


def test_enum_str():
    '''test the stringification of an enum'''
    class Test(Enum):
        '''mixture of string and non string values'''
        _1 = 'One'
        _2 = 2

    x = Test('One')
    assert x.value == rune_str(x)

    x = Test(2)
    assert '2' == rune_str(x)



if __name__ == '__main__':
    test_simple_conv()
    test_enum_str()

# EOF
