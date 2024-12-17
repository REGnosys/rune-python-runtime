'''test module for the annotated base rune types'''
from datetime import date, time, datetime
import json
import pytest
from typing_extensions import Annotated
from pydantic import Field, ValidationError

from rune.runtime.utils import BaseDataClass
from rune.runtime.annotated_base_types import NumberWithMeta
from rune.runtime.annotated_base_types import DateWithMeta
from rune.runtime.annotated_base_types import DateTimeWithMeta
from rune.runtime.annotated_base_types import TimeWithMeta
from rune.runtime.annotated_base_types import StrWithMeta


class AnnotatedStringModel(BaseDataClass):
    '''string test class'''
    # currency: Annotated[
    #     StrWithMeta,
    #     PlainSerializer(partial(MetaDataMixin.serialise, base_type=str),
    #                     return_type=dict),
    #     PlainValidator(partial(MetaDataMixin.deserialize,
    #                            base_types=str,
    #                            meta_type=StrWithMeta,
    #                            allowed_meta={'@scheme'}),
    #                    json_schema_input_type=str | dict)] = Field(
    #                        ..., description="Test currency")
    currency: Annotated[StrWithMeta,
                        StrWithMeta.plain_serializer(),
                        StrWithMeta.plain_validator(('@scheme',))
    ] = Field(..., description="Test currency")


class AnnotatedNumberModel(BaseDataClass):
    '''number test class'''
    # amount: Annotated[
    #     NumberWithMeta,
    #     PlainSerializer(partial(MetaDataMixin.serialise, base_type=Decimal),
    #                     return_type=dict),
    #     PlainValidator(partial(MetaDataMixin.deserialize,
    #                            base_types=(Decimal, float, int, str),
    #                            meta_type=NumberWithMeta,
    #                            allowed_meta={'@scheme'}),
    #                    json_schema_input_type=float | int | str
    #                    | dict)] = Field(..., description="Test amount")
    amount: Annotated[NumberWithMeta,
                      NumberWithMeta.plain_serializer(),
                      NumberWithMeta.plain_validator(('@scheme',))
    ] = Field(..., description="Test amount")


class AnnotatedDateModel(BaseDataClass):
    '''date test class'''
    # date: Annotated[
    #     DateWithMeta,
    #     PlainSerializer(partial(MetaDataMixin.serialise, base_type=str),
    #                     return_type=dict),
    #     PlainValidator(partial(MetaDataMixin.deserialize,
    #                            base_types=str,
    #                            meta_type=DateWithMeta,
    #                            allowed_meta={'@scheme'}),
    #                    json_schema_input_type=str | dict)] = Field(
    #                        ..., description="Test date")
    date: Annotated[DateWithMeta,
                    DateWithMeta.plain_serializer(),
                    DateWithMeta.plain_validator(('@scheme',))
    ] = Field(..., description="Test date")


class AnnotatedDateTimeModel(BaseDataClass):
    '''datetime test class'''
    # datetime: Annotated[
    #     DateTimeWithMeta,
    #     PlainSerializer(partial(MetaDataMixin.serialise, base_type=str),
    #                     return_type=dict),
    #     PlainValidator(partial(MetaDataMixin.deserialize,
    #                            base_types=str,
    #                            meta_type=DateTimeWithMeta,
    #                            allowed_meta={'@scheme'}),
    #                    json_schema_input_type=str | dict)] = Field(
    #                        ..., description="Test datetime")
    datetime: Annotated[DateTimeWithMeta,
                        DateTimeWithMeta.plain_serializer(),
                        DateTimeWithMeta.plain_validator(('@scheme',))
    ] = Field(..., description="Test datetime")


class AnnotatedTimeModel(BaseDataClass):
    '''datetime test class'''
    # time: Annotated[
    #     TimeWithMeta,
    #     PlainSerializer(partial(MetaDataMixin.serialise, base_type=str),
    #                     return_type=dict),
    #     PlainValidator(partial(MetaDataMixin.deserialize,
    #                            base_types=str,
    #                            meta_type=TimeWithMeta,
    #                            allowed_meta={'@scheme'}),
    #                    json_schema_input_type=str | dict)] = Field(
    #                        ..., description="Test datetime")
    time: Annotated[TimeWithMeta,
                    TimeWithMeta.plain_serializer(),
                    TimeWithMeta.plain_validator(('@scheme',))
    ] = Field(..., description="Test time")


class StrWithMetaModel(BaseDataClass):
    '''generic meta support test case'''
    # currency: Annotated[
    #     StrWithMeta,
    #     PlainSerializer(partial(MetaDataMixin.serialise, base_type=str),
    #                     return_type=dict),
    #     PlainValidator(partial(MetaDataMixin.deserialize,
    #                            base_types=str,
    #                            meta_type=StrWithMeta,
    #                            allowed_meta={'@scheme', '@key'}),
    #                    json_schema_input_type=str | dict)] = Field(
    #                        ..., description="Test currency")
    currency: Annotated[StrWithMeta,
                        StrWithMeta.plain_serializer(),
                        StrWithMeta.plain_validator(('@scheme', '@key'))
    ] = Field(..., description="Test currency")


def test_dump_annotated_string_simple():
    '''test the annotated string'''
    model = AnnotatedStringModel(currency='EUR')
    json_str = model.model_dump_json(exclude_unset=True)
    assert json_str == '{"currency":{"@data":"EUR"}}', 'explicit string failed'

    model = AnnotatedStringModel(currency=StrWithMeta('EUR'))
    json_str = model.model_dump_json(exclude_unset=True)
    assert json_str == '{"currency":{"@data":"EUR"}}', 'annotated string failed'


def test_annotated_string_with_forbidden_meta():
    '''test exception when extra meta is passed'''
    with pytest.raises(ValidationError):
        AnnotatedStringModel(currency=StrWithMeta(
            'EUR', scheme='http://fpml.org', key='currency-1'))


def test_dump_annotated_string_scheme():
    '''test the scheme treatment'''
    model = AnnotatedStringModel(
        currency=StrWithMeta('EUR', scheme='http://fpml.org'))
    json_str = model.model_dump_json(exclude_unset=True)
    assert (
        json_str == '{"currency":{"@scheme":"http://fpml.org","@data":"EUR"}}')


def test_load_annotated_string_simple():
    '''test the loading of annotated strings'''
    simple_json = '{"currency":{"@data":"EUR"}}'
    model = AnnotatedStringModel.model_validate_json(simple_json)
    assert model.currency == 'EUR', 'currency differs'
    assert model.currency.get_meta('@scheme') is None, 'scheme is not None'


def test_load_annotated_string_scheme():
    '''test the loading of annotated with a scheme strings'''
    scheme_json = '{"currency":{"@data":"EUR","@scheme":"http://fpml.org"}}'
    model = AnnotatedStringModel.model_validate_json(scheme_json)
    assert model.currency == 'EUR', 'currency differs'
    assert model.currency.get_meta('@scheme') == 'http://fpml.org'


def test_dump_annotated_number_simple():
    '''test the annotated string'''
    model = AnnotatedNumberModel(amount=10)
    json_str = model.model_dump_json(exclude_unset=True)
    assert json_str == '{"amount":{"@data":"10"}}', 'explicit int failed'

    model = AnnotatedNumberModel(amount="10.3")
    json_str = model.model_dump_json(exclude_unset=True)
    assert json_str == '{"amount":{"@data":"10.3"}}', 'explicit string failed'

    model = AnnotatedNumberModel(amount=NumberWithMeta(10))
    json_str = model.model_dump_json(exclude_unset=True)
    assert json_str == '{"amount":{"@data":"10"}}', 'annotated number failed'


def test_dump_annotated_number_scheme():
    '''test the annotated string'''
    model = AnnotatedNumberModel(
        amount=NumberWithMeta(10, scheme='http://fpml.org'))
    json_str = model.model_dump_json(exclude_unset=True)
    assert json_str == '{"amount":{"@scheme":"http://fpml.org","@data":"10"}}'


def test_load_annotated_number():
    '''test the loading of annotated with a scheme strings'''
    scheme_json = '{"amount":{"@data":"10"}}'
    model = AnnotatedNumberModel.model_validate_json(scheme_json)
    assert model.amount == 10, 'string amount differs'

    scheme_json = '{"amount":{"@data":10}}'
    model = AnnotatedNumberModel.model_validate_json(scheme_json)
    assert model.amount == 10, 'int amount differs'

    scheme_json = '{"amount":{"@data":10.3}}'
    model = AnnotatedNumberModel.model_validate_json(scheme_json)
    assert model.amount == 10.3, 'float amount differs'


def test_load_annotated_number_scheme():
    '''test the loading of annotated with a scheme strings'''
    scheme_json = '{"amount":{"@data":"10","@scheme":"http://fpml.org"}}'
    model = AnnotatedNumberModel.model_validate_json(scheme_json)
    assert model.amount == 10, 'amount differs'
    assert model.amount.get_meta('@scheme') == 'http://fpml.org'


def test_dump_annotated_date_simple():
    '''test the annotated string'''
    model = AnnotatedDateModel(date="2024-10-10")
    json_str = model.model_dump_json(exclude_unset=True)
    assert json_str == '{"date":{"@data":"2024-10-10"}}'

    model = AnnotatedDateModel(date=DateWithMeta("2024-10-10"))
    json_str = model.model_dump_json(exclude_unset=True)
    assert json_str == '{"date":{"@data":"2024-10-10"}}'


def test_load_annotated_date_scheme():
    '''test the loading of annotated with a scheme strings'''
    scheme_json = '{"date":{"@data":"2024-10-10","@scheme":"http://fpml.org"}}'
    model = AnnotatedDateModel.model_validate_json(scheme_json)
    assert model.date == date(2024, 10, 10), 'date differs'
    assert model.date.get_meta('scheme') == 'http://fpml.org', 'scheme differs'


def test_dump_annotated_datetime_simple():
    '''test the annotated string'''
    model = AnnotatedDateTimeModel(datetime="2024-10-10T01:01:01")
    json_str = model.model_dump_json(exclude_unset=True)
    assert json_str == '{"datetime":{"@data":"2024-10-10T01:01:01"}}'

    model = AnnotatedDateTimeModel(
        datetime=DateTimeWithMeta("2024-10-10T01:01:01"))
    json_str = model.model_dump_json(exclude_unset=True)
    assert json_str == '{"datetime":{"@data":"2024-10-10T01:01:01"}}'


def test_load_annotated_datetime_scheme():
    '''test the loading of annotated with a scheme strings'''
    scheme_json = ('{"datetime":{"@data":"2024-10-10T01:01:01",'
                   '"@scheme":"http://fpml.org"}}')
    model = AnnotatedDateTimeModel.model_validate_json(scheme_json)
    assert model.datetime == datetime(2024, 10, 10, 1, 1, 1), 'datetime differs'
    assert model.datetime.get_meta('scheme') == 'http://fpml.org'


def test_dump_annotated_time_simple():
    '''test the annotated string'''
    model = AnnotatedTimeModel(time="01:01:01.000087")
    json_str = model.model_dump_json(exclude_unset=True)
    assert json_str == '{"time":{"@data":"01:01:01.000087"}}'

    model = AnnotatedTimeModel(time=TimeWithMeta("01:01:01"))
    json_str = model.model_dump_json(exclude_unset=True)
    assert json_str == '{"time":{"@data":"01:01:01"}}'


def test_load_annotated_time_scheme():
    '''test the loading of annotated with a scheme strings'''
    scheme_json = (
        '{"time":{"@data":"01:01:01.000087","@scheme":"http://fpml.org"}}')
    model = AnnotatedTimeModel.model_validate_json(scheme_json)
    assert model.time == time(1, 1, 1, 87), 'time differs'
    assert model.time.get_meta('scheme') == 'http://fpml.org', 'scheme differs'


def test_generic_string_with_meta():
    '''generic meta support'''
    model = StrWithMetaModel(currency='EUR')
    assert model.currency == 'EUR'

    model = StrWithMetaModel(currency=StrWithMeta(
        'EUR', scheme='http://fpml.org', key='currency-1'))
    assert model.currency == 'EUR'
    # pylint: disable=no-member
    assert model.currency.get_meta('@scheme') == 'http://fpml.org'
    assert model.currency.get_meta('@key') == 'currency-1'

    json_str = model.model_dump_json(exclude_unset=True)
    j_dict = json.loads(json_str)
    assert j_dict['currency']['@data'] == 'EUR'
    assert j_dict['currency']['@scheme'] == 'http://fpml.org'
    assert j_dict['currency']['@key'] == 'currency-1'


def test_load_generic_string_with_meta():
    '''load json with generic meta support'''
    simple_json = (
        '{"currency":{"@data":"EUR","@scheme":"http://fpml.org",'
        '"@key":"currency-1"}}'
    )
    model = StrWithMetaModel.model_validate_json(simple_json)
    assert model.currency == 'EUR'
    assert model.currency.get_meta('@scheme') == 'http://fpml.org'
    assert model.currency.get_meta('@key') == 'currency-1'


def test_generic_string_with_forbidden_meta():
    '''test exception when extra meta is passed'''
    with pytest.raises(ValidationError):
        StrWithMetaModel(currency=StrWithMeta(
            'EUR', scheme='http://fpml.org', key='currency-1', ref='blah'))

# EOF
