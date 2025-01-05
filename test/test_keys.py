'''test key generation/retrieval runtime functions'''
from decimal import Decimal
from typing_extensions import Annotated
import pytest
from pydantic import Field

from rune.runtime.base_data_class import BaseDataClass
from rune.runtime.metadata import Reference


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

# EOF
