'''test module for the parametrized rune basic types'''
from decimal import Decimal
import pytest
from pydantic import Field, ValidationError

from rune.runtime.utils import BaseDataClass


class NumberWithConstraintsModel(BaseDataClass):
    '''test class for parametrized numbers'''
    amount: Decimal = Field(...,
                            description='a test amount',
                            max_digits=5,
                            decimal_places=3,
                            ge=0,
                            le=98)


class StringWithConstraintsModel(BaseDataClass):
    '''string constraints test case'''
    currency: str = Field(...,
                          description="Test currency",
                          min_length=3,
                          max_length=5,
                          pattern=r'^[A-Z]*$')


def test_excess_decimal_places_number():
    '''test various conditions'''
    with pytest.raises(ValidationError):
        NumberWithConstraintsModel(amount=1.2001)


def test_excess_max_digits_number():
    """ should fail as decimal is 3 and max digits is 5 - digits can't be more
        than 2
    """
    with pytest.raises(ValidationError):
        NumberWithConstraintsModel(amount=100)


def test_excess_max_val():
    '''test max value condition'''
    with pytest.raises(ValidationError):
        NumberWithConstraintsModel(amount=98.1)


def test_excess_min_val():
    '''test max value condition'''
    with pytest.raises(ValidationError):
        NumberWithConstraintsModel(amount=-1)


def test_create_str_model():
    '''test the creation of the constrained str model'''
    model = StringWithConstraintsModel(currency='EUR')
    assert model.currency == 'EUR'


def test_fail_min_create_constrained_str_model():
    '''test the creation of the constrained str model'''
    with pytest.raises(ValidationError):
        StringWithConstraintsModel(currency='EU')


def test_fail_max_create_constrained_str_model():
    '''test the creation of the constrained str model'''
    with pytest.raises(ValidationError):
        StringWithConstraintsModel(currency='EUROOO')


def test_fail_pattern_create_constrained_str_model():
    '''test the creation of the constrained str model'''
    with pytest.raises(ValidationError):
        StringWithConstraintsModel(currency='EUR1')

# EOF
