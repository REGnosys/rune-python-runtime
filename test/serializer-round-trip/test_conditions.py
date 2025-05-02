# pylint: disable=invalid-name
'''testing basic conditions compliance'''
import datetime
import pytest
from pydantic import Field, ValidationError
from rune.runtime.base_data_class import BaseDataClass


class cdm_base_datetime_DateList(BaseDataClass):
    """
    List of dates.
    """
    _FQRTN = 'cdm.base.datetime.DateList'
    date: list[datetime.date] = Field(..., description='', min_length=1)


def test_min_list_length_all_defaults():
    '''no doc'''
    with pytest.raises(ValidationError):
        cdm_base_datetime_DateList()


def test_min_list_length_empty_list():
    '''no doc'''
    with pytest.raises(ValidationError):
        cdm_base_datetime_DateList(date=[])

# EOF
