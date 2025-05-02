'''
Testing basic types using the following Rune definitions:

typeAlias ParameterisedNumberType:
    number(digits: 18, fractionalDigits: 2)

typeAlias ParameterisedStringType:
    string(minLength: 1, maxLength: 20, pattern: "[a-zA-Z]")

type BasicSingle:
  booleanType boolean (1..1)
  numberType number (1..1)
  parameterisedNumberType ParameterisedNumberType (1..1)
  parameterisedStringType ParameterisedStringType (1..1)
  stringType string (1..1)
  timeType time (1..1)

type BasicList:
  booleanTypes boolean (1..*)
  numberTypes number (1..*)
  parameterisedNumberTypes ParameterisedNumberType (1..*)
  parameterisedStringTypes ParameterisedStringType (1..*)
  stringTypes string (1..*)
  timeTypes time (1..*)

type Root:
  [rootType]
  basicSingle BasicSingle (0..1)
  basicList BasicList (0..1)

'''
import datetime
from decimal import Decimal
from typing import Optional, Annotated
from pydantic import Field
from rune.runtime.base_data_class import BaseDataClass
# from rune.runtime.metadata import NumberWithMeta
# pylint: disable=invalid-name


class BasicSingle(BaseDataClass):
    '''no doc'''
    booleanType: bool = Field(..., description='')
    numberType: Decimal = Field(..., description='')
    parameterisedNumberType: Decimal = Field(...,
                                             description='',
                                             max_digits=18,
                                             decimal_places=2)
    # NOTE: the addition of a prefix and suffix to the regular expression!!!
    parameterisedStringType: str = Field(...,
                                         description='',
                                         min_length=1,
                                         max_length=20,
                                         pattern=r'^[a-zA-Z]*$')
    stringType: str = Field(..., description='')
    timeType: datetime.time = Field(..., description='')


class BasicList(BaseDataClass):
    '''no doc'''
    booleanTypes: list[bool] = Field([], description='', min_length=1)
    numberTypes: list[Decimal] = Field([], description='', min_length=1)
    # parameterisedNumberTypes: list[Annotated[
    #     NumberWithMeta,
    #     NumberWithMeta.serializer(),
    #     NumberWithMeta.validator(('@ref', )),
    #     Field(decimal_places=2, max_digits=6)]] = Field(
    #         [],
    #         description='',
    #         min_length=1
    #     )
    parameterisedNumberTypes: list[Annotated[
        Decimal,
        Field(decimal_places=2, max_digits=5)]] = Field([],
                                                        description='',
                                                        min_length=1)
    # NOTE: the addition of a prefix and suffix to the regular expression!!!
    parameterisedStringTypes: list[Annotated[
        str,
        Field(min_length=1, max_length=20, pattern=r'^[a-zA-Z]*$')]] = Field(
            [], description='', min_length=1)
    stringTypes: list[str] = Field([], description='', min_length=1)
    timeTypes: list[datetime.time] = Field([], description='', min_length=1)


class Root(BaseDataClass):
    '''no doc'''
    basicSingle: Optional[BasicSingle] = Field(None, description='')
    basicList: Optional[BasicList] = Field(None, description='')


def test_basic_types_single():
    '''basic-types-single.json'''
    json_str = '''
        {
            "basicSingle" : {
                "booleanType" : true,
                "numberType" : 123.456,
                "parameterisedNumberType" : 123.99,
                "parameterisedStringType" : "abcDEF",
                "stringType" : "foo",
                "timeType" : "12:00:00"
            }
        }
    '''
    model = Root.model_validate_json(json_str)
    model.validate_model()


def test_basic_types_list():
    '''basic-types-list.json'''
    json_str = '''
        {
            "basicList" : {
                "booleanTypes" : [ true, false, true ],
                "numberTypes" : [ 123.456, 789, 345.123 ],
                "parameterisedNumberTypes" : [ 123.99, 456, 99.12 ],
                "parameterisedStringTypes" : [ "abcDEF", "foo", "foo" ],
                "stringTypes" : [ "foo", "bar", "Baz123" ],
                "timeTypes" : [ "12:00:00" ]
            }
        }
    '''
    model = Root.model_validate_json(json_str)
    model.validate_model()

# EOF
