'''test key generation/retrieval runtime functions'''
from decimal import Decimal
from typing_extensions import Annotated
import pytest
from pydantic import Field

from rune.runtime.base_data_class import BaseDataClass
from rune.runtime.metadata import Reference
from rune.runtime.metadata import NumberWithMeta, StrWithMeta


class CashFlow(BaseDataClass):
    '''test cashflow'''
    currency: str = Field(...,
                          description='currency',
                          min_length=3,
                          max_length=3)
    amount: Decimal = Field(..., description='payment amount', ge=0)


class DummyLoan(BaseDataClass):
    '''some more complex data structure'''
    loan: CashFlow = Field(..., description='loaned amount')
    repayment: CashFlow = Field(..., description='repaid amount')


class DummyLoan2(BaseDataClass):
    '''some more complex data structure'''
    loan: Annotated[CashFlow,
                    CashFlow.serializer(),
                    CashFlow.validator(allowed_meta=('@key', '@ref'))] = Field(
                        ..., description='loaned amount')
    repayment: Annotated[CashFlow,
                         CashFlow.serializer(),
                         CashFlow.validator(
                             allowed_meta=('@key', '@ref'))] = Field(
                                 ..., description='repaid amount')


class DummyLoan3(BaseDataClass):
    '''number test class'''
    loan: Annotated[NumberWithMeta,
                    NumberWithMeta.serializer(),
                    NumberWithMeta.validator(
                        ('@key', ))] = Field(...,
                                             description="Test amount",
                                             decimal_places=3)
    repayment: Annotated[NumberWithMeta,
                         NumberWithMeta.serializer(),
                         NumberWithMeta.validator(
                             ('@ref', ))] = Field(...,
                                                  description="Test amount",
                                                  decimal_places=3)


class DummyTradeParties(BaseDataClass):
    '''number test class'''
    party1: Annotated[StrWithMeta,
                      StrWithMeta.serializer(),
                      StrWithMeta.validator(
                          ('@key', ))] = Field(..., description="cpty1")
    party2: Annotated[StrWithMeta,
                      StrWithMeta.serializer(),
                      StrWithMeta.validator(
                          ('@ref', ))] = Field(...,
                                               description="cpty2")


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
    model.bind_property_to('repayment', key)
    assert id(model.loan) == id(model.repayment)


def test_use_ref_from_object():
    '''test use a ref'''
    model = DummyLoan2(loan=CashFlow(currency='EUR', amount=100),
                       repayment=CashFlow(currency='EUR', amount=101))
    model.bind_property_to('repayment', model.loan)
    assert id(model.loan) == id(model.repayment)


def test_bad_key_generation():
    '''generate a key for an object which can't be referenced'''
    model = DummyLoan(loan=CashFlow(currency='EUR', amount=100),
                      repayment=CashFlow(currency='EUR', amount=101))
    with pytest.raises(ValueError):
        model.loan.get_or_create_key()  # pylint: disable=no-member


def test_invalid_property():
    '''Attempts to bind a property when not allowed'''
    model = DummyLoan(loan=CashFlow(currency='EUR', amount=100),
                      repayment=CashFlow(currency='EUR', amount=101))
    model2 = DummyLoan2(loan=CashFlow(currency='EUR', amount=100),
                        repayment=CashFlow(currency='EUR', amount=101))

    with pytest.raises(ValueError):
        model.bind_property_to('repayment', model2.loan)


def test_ref_assign():
    '''test use a ref'''
    model = DummyLoan2(loan=CashFlow(currency='EUR', amount=100),
                       repayment=CashFlow(currency='EUR', amount=101))
    model.repayment = Reference(model.loan)
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

# EOF
