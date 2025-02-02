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
def test_address():
    '''no doc'''
    json_str = '''    {
        "@model": "serialization",
        "@type": "serialization.test.metalocation.Root",
        "@version": "0.0.0",
        "typeA": {
            "b": {
                "fieldB": "foo",
                "@key:scoped": "someLocation"
            }
        },
        "bAddress": {
            "@ref:scoped": "someLocation"
        }
    }'''
    model = BaseDataClass.rune_deserialize(json_str)
    resp_json = model.rune_serialize()
    assert json.loads(resp_json) == json.loads(json_str)

# EOF
