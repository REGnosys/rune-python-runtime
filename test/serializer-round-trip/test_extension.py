'''tests based on the extension folder in rune-serializer-round-trip-test'''
# pylint: disable=import-outside-toplevel
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
def test_base_type():
    '''no doc'''
    json_str = '''{
        "@model": "serialization",
        "@type": "serialization.test.passing.extension.Root",
        "@version": "0.0.0",
        "typeA": {
            "fieldA": "foo"
        }
    }'''
    model = BaseDataClass.rune_deserialize(json_str)
    resp_json = model.rune_serialize()
    assert json.loads(resp_json) == json.loads(json_str)


@pytest.mark.skipif(NO_SER_TEST_MOD, reason='Generated test package not found')
def test_extended_type_concrete():
    '''no doc'''
    json_str = '''{
        "@model": "serialization",
        "@type": "serialization.test.passing.extension.Root",
        "@version": "0.0.0",
        "typeB": {
            "fieldA": "foo",
            "fieldB": "foo",
            "@type": "serialization.test.passing.extension.B"
        }
    }'''
    model = BaseDataClass.rune_deserialize(json_str)
    resp_json = model.rune_serialize()
    org_dict = json.loads(json_str)
    org_dict['typeB'].pop('@type')
    assert org_dict == json.loads(resp_json)
    # assert json.loads(resp_json) == json.loads(json_str)


@pytest.mark.skipif(NO_SER_TEST_MOD, reason='Generated test package not found')
def test_extended_type_polymorphic():
    '''no doc'''
    json_str = '''{
        "@model": "serialization",
        "@type": "serialization.test.passing.extension.Root",
        "@version": "0.0.0",
        "typeA": {
            "fieldA": "bar",
            "fieldB": "foo",
            "@type": "serialization.test.passing.extension.B"
        }
    }'''
    # import serialization.test.passing.extension.Root
    model = BaseDataClass.rune_deserialize(json_str)
    resp_json = model.rune_serialize()
    assert json.loads(resp_json) == json.loads(json_str)


@pytest.mark.skipif(NO_SER_TEST_MOD, reason='Generated test package not found')
def test_at_type():
    '''no doc'''
    from serialization.test.passing.extension.B import B
    json_str = '''
        {
            "@type": "serialization.test.passing.extension.Root",
            "typeA" : {
                "fieldA" : "bar",
                "fieldB" : "foo",
                "@type" : "serialization.test.passing.extension.B"
            }
        }
    '''
    model = BaseDataClass.rune_deserialize(json_str)
    assert isinstance(model.typeA, B)


@pytest.mark.skipif(NO_SER_TEST_MOD, reason='Generated test package not found')
def test_temp():
    '''no doc'''
    from serialization.test.passing.metakey.Root import Root
    json_str = '''
    {
        "nodeRef" : {
            "typeA" : {
                "fieldA" : "foo",
                "@key" : "someKey1x"
            },
            "aReference" : {
                "@ref" : "someKey1x"
            }
        }
    }
    '''
    model = Root.model_validate_json(json_str)
    assert id(model.nodeRef.typeA) == id(model.nodeRef.aReference)


@pytest.mark.skipif(NO_SER_TEST_MOD, reason='Generated test package not found')
def test_enums():
    '''no doc'''
    from serialization.test.passing.enumtypes.Root import Root
    json_str = '{"enumSingle":{"enumType":"A"}}'
    json_dict = json.loads(json_str)
    model1 = Root.model_validate(json_dict)
    model2 = Root.model_validate_json(json_str)
    model1.validate_model()
    model2.validate_model()
    resp_json1 = model1.model_dump_json(exclude_unset=True)
    resp_json2 = model2.model_dump_json(exclude_unset=True)
    assert resp_json1 == json_str
    assert resp_json2 == json_str

# EOF
