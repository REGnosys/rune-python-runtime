'''Full attribute validation - pydantic and constraints'''
import pytest
from pydantic import ValidationError
try:
    # pylint: disable=unused-import
    # type: ignore
    from cdm.base.math.NonNegativeQuantity import NonNegativeQuantity
    from cdm.base.math.UnitType import UnitType
    NO_SER_TEST_MOD = False
except ImportError:
    NO_SER_TEST_MOD = True


@pytest.mark.skipif(NO_SER_TEST_MOD, reason='CDM package not found')
def test_bad_attrib_validation():
    '''Invalid attribute assigned'''
    unit = UnitType(currency='EUR')
    mq = NonNegativeQuantity(value=10, unit=unit)
    mq.frequency = 'Blah'
    with pytest.raises(ValidationError):
        mq.validate_model()

# EOF
