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
def test_enum_types_single():
    '''no doc'''
    # import serialization.test.passing.enumtypes.Root
    # import serialization.test.passing.enumtypes.EnumSingle
    # import serialization.test.passing.enumtypes.EnumType

    # root = serialization.test.passing.enumtypes.Root.Root(
    #     enumSingle=serialization.test.passing.enumtypes.EnumSingle.EnumSingle(
    #         enumType=serialization.test.passing.enumtypes.EnumType.EnumType.A
    #     ))
    # resp_json = root.rune_serialize()
    json_str = '''
        {
            "@model": "serialization",
            "@type": "serialization.test.passing.enumtypes.Root",
            "@version": "0.0.0",
            "enumSingle": {
                "enumType": "A"
            }
        }
    '''
    model = BaseDataClass.rune_deserialize(json_str)
    resp_json = model.rune_serialize()
    assert json.loads(resp_json) == json.loads(json_str)


@pytest.mark.skipif(NO_SER_TEST_MOD, reason='Generated test package not found')
def test_enum_types_list():
    '''no doc'''
    json_str = '''
        {
            "@model": "serialization",
            "@type": "serialization.test.passing.enumtypes.Root",
            "@version": "0.0.0",
            "enumList": {
                "enumType": ["A", "B", "C", "B"]
            }
        }
    '''
    model = BaseDataClass.rune_deserialize(json_str)
    resp_json = model.rune_serialize()
    assert json.loads(resp_json) == json.loads(json_str)

# EOF
