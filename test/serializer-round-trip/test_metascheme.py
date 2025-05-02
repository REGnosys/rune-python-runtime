'''Serialization Enum tests'''
import json
import pytest
from rune.runtime.base_data_class import BaseDataClass

try:
    # pylint: disable=unused-import
    # type: ignore
    import serialization  # noqa
    NO_SER_TEST_MOD = False
except ImportError:
    NO_SER_TEST_MOD = True


@pytest.mark.skipif(NO_SER_TEST_MOD, reason='Generated test package not found')
def test_enum_single():
    '''enums with meta'''
    json_str = '''
        {
            "@model": "serialization",
            "@type": "serialization.test.passing.metascheme.Root",
            "@version": "0.0.0",
            "enumType": {
                "@data": "A",
                "@scheme": "https://www.example.com/scheme"
            }
        }
    '''
    model = BaseDataClass.rune_deserialize(json_str)
    resp_json = model.rune_serialize()
    assert json.loads(resp_json) == json.loads(json_str)


@pytest.mark.skipif(NO_SER_TEST_MOD, reason='Generated test package not found')
def test_enum_list():
    '''list of enums with meta'''
    json_str = '''
    {
        "@model": "serialization",
        "@type": "serialization.test.passing.metascheme.Root",
        "@version": "0.0.0",
        "enumTypeList": [{
            "@data": "A",
            "@scheme": "https://www.example.com/scheme1"
        }, {
            "@data": "B",
            "@scheme": "https://www.example.com/scheme2"
        }, {
            "@data": "C",
            "@scheme": "https://www.example.com/scheme3"
        }]
    }
    '''
    model = BaseDataClass.rune_deserialize(json_str)
    resp_json = model.rune_serialize()
    assert json.loads(resp_json) == json.loads(json_str)

# EOF
