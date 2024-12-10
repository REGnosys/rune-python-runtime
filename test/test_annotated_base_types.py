'''test module for the annotated base rune types'''
from rune.runtime.utils import BaseDataClass
from rune.runtime.annotated_base_types import AnnotatedString
from rune.runtime.annotated_base_types import AnnotatedStringProperty
from rune.runtime.annotated_base_types import AnnotatedNumber
from rune.runtime.annotated_base_types import AnnotatedNumberProperty


class AnnotatedStringModel(BaseDataClass):
    '''string test class'''
    currency: AnnotatedStringProperty


class AnnotatedNumberModel(BaseDataClass):
    '''number test class'''
    amount: AnnotatedNumberProperty


def test_dump_annotated_string_simple():
    '''test the annotated string'''
    model = AnnotatedStringModel(currency='EUR')
    json_str = model.model_dump_json(exclude_unset=True)
    assert json_str == '{"currency":{"@data":"EUR"}}', 'explicit string failed'

    model = AnnotatedStringModel(currency=AnnotatedString('EUR'))
    json_str = model.model_dump_json(exclude_unset=True)
    assert json_str == '{"currency":{"@data":"EUR"}}', 'annotated string failed'


def test_dump_annotated_string_scheme():
    '''test the scheme treatment'''
    model = AnnotatedStringModel(
        currency=AnnotatedString('EUR', scheme='http://fpml.org'))
    json_str = model.model_dump_json(exclude_unset=True)
    assert (
        json_str == '{"currency":{"@data":"EUR","@scheme":"http://fpml.org"}}')


def test_load_annotated_string_simple():
    '''test the loading of annotated strings'''
    simple_json = '{"currency":{"@data":"EUR"}}'
    model = AnnotatedStringModel.model_validate_json(simple_json)
    assert model.currency == 'EUR', 'currency differs'
    assert model.currency.scheme is None, 'scheme is not None'


def test_load_annotated_string_scheme():
    '''test the loading of annotated with a scheme strings'''
    scheme_json = '{"currency":{"@data":"EUR","@scheme":"http://fpml.org"}}'
    model = AnnotatedStringModel.model_validate_json(scheme_json)
    assert model.currency == 'EUR', 'currency differs'
    assert model.currency.scheme == 'http://fpml.org', 'scheme differs'


def test_dump_annotated_number_simple():
    '''test the annotated string'''
    model = AnnotatedNumberModel(amount=10)
    json_str = model.model_dump_json(exclude_unset=True)
    assert json_str == '{"amount":{"@data":"10"}}', 'explicit int failed'

    model = AnnotatedNumberModel(amount="10.3")
    json_str = model.model_dump_json(exclude_unset=True)
    assert json_str == '{"amount":{"@data":"10.3"}}', 'explicit string failed'

    model = AnnotatedNumberModel(amount=AnnotatedNumber(10))
    json_str = model.model_dump_json(exclude_unset=True)
    assert json_str == '{"amount":{"@data":"10"}}', 'annotated number failed'


def test_dump_annotated_number_scheme():
    '''test the annotated string'''
    model = AnnotatedNumberModel(
        amount=AnnotatedNumber(10, scheme='http://fpml.org'))
    json_str = model.model_dump_json(exclude_unset=True)
    assert json_str == '{"amount":{"@data":"10","@scheme":"http://fpml.org"}}'


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
    assert model.amount.scheme == 'http://fpml.org', 'scheme differs'

# EOF
