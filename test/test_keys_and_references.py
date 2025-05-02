'''test key generation/retrieval runtime functions'''
from decimal import Decimal
from typing_extensions import Annotated
import pytest
from pydantic import Field, ValidationError

from rune.runtime.base_data_class import BaseDataClass
from rune.runtime.metadata import Reference, KeyType
from rune.runtime.metadata import NumberWithMeta, StrWithMeta


class CashFlow(BaseDataClass):
    '''test cashflow'''
    _ALLOWED_METADATA = {'@key', '@key:external'}
    currency: str = Field(...,
                          description='currency',
                          min_length=3,
                          max_length=3)
    amount: Decimal = Field(..., description='payment amount', ge=0)


class CashFlowNoKey(BaseDataClass):
    '''test cashflow'''
    currency: str = Field(...,
                          description='currency',
                          min_length=3,
                          max_length=3)
    amount: Decimal = Field(..., description='payment amount', ge=0)


class DummyLoanNoKey(BaseDataClass):
    '''some more complex data structure'''
    loan: CashFlowNoKey = Field(..., description='loaned amount')
    repayment: CashFlowNoKey = Field(..., description='repaid amount')


class DummyLoan(BaseDataClass):
    '''some more complex data structure'''
    loan: CashFlow = Field(..., description='loaned amount')
    repayment: CashFlow = Field(..., description='repaid amount')


class DummyLoan2(BaseDataClass):
    '''some more complex data structure'''
    loan: Annotated[CashFlow,
                    CashFlow.serializer(),
                    CashFlow.validator(
                        allowed_meta=('@key', '@key:external', '@ref:external',
                                      '@ref'))] = Field(
                                          ..., description='loaned amount')
    repayment: Annotated[CashFlow,
                         CashFlow.serializer(),
                         CashFlow.validator(
                             allowed_meta=('@key', '@key:external',
                                           '@ref:external', '@ref'))] = Field(
                                               ...,
                                               description='repaid amount')

    _KEY_REF_CONSTRAINTS = {
        'loan': {'@ref', '@ref:external'},
        'repayment': {'@ref', '@ref:external'}
    }

class DummyLoan3(BaseDataClass):
    '''number test class'''
    loan: Annotated[NumberWithMeta,
                    NumberWithMeta.serializer(),
                    NumberWithMeta.validator(
                        ('@key', '@key:external'))] = Field(...,
                                             description="Test amount",
                                             decimal_places=3)
    repayment: Annotated[NumberWithMeta,
                         NumberWithMeta.serializer(),
                         NumberWithMeta.validator(
                             ('@ref', '@ref:external'))] = Field(...,
                                                  description="Test amount",
                                                  decimal_places=3)

    _KEY_REF_CONSTRAINTS = {
        'loan': {'@ref', '@ref:external'},
        'repayment': {'@ref', '@ref:external'}
    }


class DummyLoan4(BaseDataClass):
    '''number test class'''
    loan: Annotated[NumberWithMeta,
                    NumberWithMeta.serializer(),
                    NumberWithMeta.validator(
                        ('@key', '@key:external'))] = Field(...,
                                             description="Test amount",
                                             decimal_places=3)
    repayment: Annotated[NumberWithMeta,
                         NumberWithMeta.serializer(),
                         NumberWithMeta.validator(
                             ('@ref', '@ref:external'))] = Field(...,
                                                  description="Test amount",
                                                  decimal_places=3, gt=0)

    _KEY_REF_CONSTRAINTS = {
        'loan': {'@ref', '@ref:external'},
        'repayment': {'@ref', '@ref:external'}
    }

class DummyTradeParties(BaseDataClass):
    '''number test class'''
    party1: Annotated[StrWithMeta,
                      StrWithMeta.serializer(),
                      StrWithMeta.validator(
                          ('@key',
                           '@key:external'))] = Field(..., description="cpty1")
    party2: Annotated[StrWithMeta,
                      StrWithMeta.serializer(),
                      StrWithMeta.validator(
                          ('@ref',
                           '@ref:external'))] = Field(..., description="cpty2")

    _KEY_REF_CONSTRAINTS = {
        'party2': {'@ref', '@ref:external'}
    }


class DummyBiLoan(BaseDataClass):
    '''more complex model'''
    loan1: DummyLoan2
    loan2: DummyLoan2


def test_key_generation():
    '''generate a key for an object'''
    model = DummyLoan2(loan=CashFlow(currency='EUR', amount=100),
                       repayment=CashFlow(currency='EUR', amount=101))
    key = model.loan.get_or_create_key()  # pylint: disable=no-member
    assert key


def test_use_ref_from_key():
    '''test use a ref'''
    model = DummyLoan2(loan=CashFlow(currency='EUR', amount=100),
                       repayment=CashFlow(currency='EUR', amount=101))
    key = model.loan.get_or_create_key()  # pylint: disable=no-member
    ref = Reference(key, key_type=KeyType.INTERNAL, parent=model)
    # pylint: disable=protected-access
    model._bind_property_to('repayment', ref)
    assert id(model.loan) == id(model.repayment)


def test_use_ref_from_object():
    '''test use a ref'''
    model = DummyLoan2(loan=CashFlow(currency='EUR', amount=100),
                       repayment=CashFlow(currency='EUR', amount=101))
    # pylint: disable=protected-access
    model._bind_property_to('repayment', Reference(model.loan))
    assert id(model.loan) == id(model.repayment)


def test_bad_key_generation():
    '''generate a key for an object which can't be referenced'''
    model = DummyLoanNoKey(loan=CashFlowNoKey(currency='EUR', amount=100),
                           repayment=CashFlowNoKey(currency='EUR', amount=101))
    with pytest.raises(ValueError):
        model.loan.get_or_create_key()  # pylint: disable=no-member


def test_invalid_property():
    '''Attempts to bind a property when not allowed'''
    model = DummyLoan(loan=CashFlow(currency='EUR', amount=100),
                      repayment=CashFlow(currency='EUR', amount=101))
    model2 = DummyLoan2(loan=CashFlow(currency='EUR', amount=100),
                        repayment=CashFlow(currency='EUR', amount=101))

    with pytest.raises(ValueError):
        # pylint: disable=protected-access
        model._bind_property_to('repayment', Reference(model2.loan))


def test_ref_assign():
    '''test use a ref'''
    model = DummyLoan2(loan=CashFlow(currency='EUR', amount=100),
                       repayment=CashFlow(currency='EUR', amount=101))
    model.repayment = Reference(model.loan)
    assert id(model.loan) == id(model.repayment)


def test_ref_in_constructor():
    '''test use a ref'''
    cf = CashFlow(currency='EUR', amount=100)
    model = DummyLoan2(loan=cf, repayment=Reference(cf))
    assert id(model.loan) == id(model.repayment)


def test_ref_re_assign():
    '''test use a ref'''
    model = DummyLoan2(loan=CashFlow(currency='EUR', amount=100),
                       repayment=CashFlow(currency='EUR', amount=101))
    old_cf = model.repayment
    model.repayment = Reference(model.loan)
    assert id(model.loan) == id(model.repayment)
    model.repayment = old_cf
    assert 'repayment' not in model.__dict__['__rune_references']
    assert id(model.repayment) == id(old_cf)


def test_ref_ext_assign():
    '''test use a ext key and ref'''
    model = DummyLoan2(loan=CashFlow(currency='EUR', amount=100),
                       repayment=CashFlow(currency='EUR', amount=101))
    model.repayment = Reference(model.loan, 'ext_key1')
    assert id(model.loan) == id(model.repayment)


def test_ref_ext_assign_2():
    '''test use a ext key and ref'''
    model = DummyLoan2(loan=CashFlow(currency='EUR', amount=100),
                       repayment=CashFlow(currency='EUR', amount=101))
    # pylint: disable=no-member
    model.loan.set_external_key('ext_key3', KeyType.EXTERNAL)
    model.repayment = Reference('ext_key3',
                                key_type=KeyType.EXTERNAL,
                                parent=model)
    assert id(model.loan) == id(model.repayment)


def test_init_ref_assign():
    '''test use a ref'''
    loan = CashFlow(currency='EUR', amount=100)
    # repayment = Reference(loan, True)
    model = DummyLoan2(loan=loan, repayment=loan)
    assert id(model.loan) == id(model.repayment)


def test_basic_ref_assign():
    '''test use a ref'''
    model = DummyLoan3(loan=100, repayment=101)
    model.repayment = Reference(model.loan)
    assert id(model.loan) == id(model.repayment)


def test_basic_str_ref_assign():
    '''test use a ref'''
    model = DummyTradeParties(party1='p1', party2='p2')
    model.party2 = Reference(model.party1)
    assert id(model.party1) == id(model.party2)


def test_dump_key_ref():
    '''test dump a ref'''
    model = DummyLoan2(loan=CashFlow(currency='EUR', amount=100),
                       repayment=CashFlow(currency='EUR', amount=101))
    model.repayment = Reference(model.loan)
    dict_ = model.model_dump(exclude_unset=True)
    assert dict_['loan']['@key'] == dict_['repayment']['@ref']
    assert len(dict_['repayment']) == 1


def test_dump_ref_ext():
    '''test use a ext key and ref'''
    model = DummyLoan2(loan=CashFlow(currency='EUR', amount=100),
                       repayment=CashFlow(currency='EUR', amount=101))
    model.repayment = Reference(model.loan, 'ext_key2')
    dict_ = model.model_dump(exclude_unset=True)
    assert dict_['loan']['@key:external'] == dict_['repayment']['@ref:external']


def test_dump_key_ref_2():
    '''test dump a ref'''
    model = DummyBiLoan(loan1=DummyLoan2(loan=CashFlow(currency='EUR',
                                                       amount=100),
                                         repayment=CashFlow(currency='EUR',
                                                            amount=101)),
                        loan2=DummyLoan2(loan=CashFlow(currency='EUR',
                                                       amount=100),
                                         repayment=CashFlow(currency='EUR',
                                                            amount=101)))
    model.loan1.repayment = Reference(model.loan1.loan)
    dict_ = model.model_dump(exclude_unset=True)
    assert dict_['loan1']['loan']['@key'] == dict_['loan1']['repayment']['@ref']
    assert len(dict_['loan1']['repayment']) == 1


def test_load_loan_with_key_ref():
    '''test load a simple model with json with some meta'''
    json_str = '''{
        "loan":{"@key":"cf-1-2","currency":"EUR","amount":"100"},
        "repayment":{"@ref":"cf-1-2"}
    }'''
    model = DummyLoan2.model_validate_json(json_str)
    assert id(model.loan) == id(model.repayment)


def test_load_basic_type_loan_with_key_ref():
    '''test load a simple model with json with some meta'''
    json_str = '''{
        "loan": {"@key":"8e50b68b-6426-44a8-bbfd-cbe3b833131c","@data":"100"},
        "repayment":{"@ref":"8e50b68b-6426-44a8-bbfd-cbe3b833131c"}
    }'''
    model = DummyLoan3.model_validate_json(json_str)
    assert id(model.loan) == id(model.repayment)


def test_load_basic_type_loan_with_key_ref_and_constraints():
    '''test load a simple model with json with some meta'''
    json_str = '''{
        "loan": {"@key":"8e50b68b-6426-44a8-bbfd-cbe3b833131a","@data":"100"},
        "repayment":{"@ref":"8e50b68b-6426-44a8-bbfd-cbe3b833131a"}
    }'''
    model = DummyLoan4.model_validate_json(json_str)
    model.validate_model()
    assert id(model.loan) == id(model.repayment)


def test_load_basic_type_loan_with_key_ref_and_broken_constraints():
    '''test load a simple model with json with some meta'''
    json_str = '''{
        "loan": {"@key":"8e50b68b-6426-44a8-bbfd-cbe3b833131b","@data":"-100"},
        "repayment":{"@ref":"8e50b68b-6426-44a8-bbfd-cbe3b833131b"}
    }'''
    model = DummyLoan4.model_validate_json(json_str)
    with pytest.raises(ValidationError):
        model.validate_model()

# EOF
