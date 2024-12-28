'''complex types tests'''
from decimal import Decimal
from typing_extensions import Annotated
import pytest
from pydantic import Field

from rune.runtime.base_data_class import BaseDataClass


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


def test_create_loan_no_meta():
    '''tests the creation of a simple model - no meta'''
    model = DummyLoan(loan=CashFlow(currency='EUR', amount=100),
                      repayment=CashFlow(currency='EUR', amount=101))
    json_str = model.model_dump_json(exclude_unset=True)
    assert json_str


def test_create_loan_no_meta_exc():
    '''tests the creation of a simple model - no meta'''
    model = DummyLoan(loan=CashFlow(currency='EUR', amount=100),
                      repayment=CashFlow(currency='EUR', amount=101))
    with pytest.raises(ValueError):
        model.loan.set_meta(key='cf-1-1')  # pylint: disable=no-member


def test_create_loan_with_meta():
    '''tests the creation of a simple model with some meta'''
    model = DummyLoan2(loan=CashFlow(currency='EUR', amount=100),
                       repayment=CashFlow(currency='EUR', amount=101))
    model.loan.set_meta(key='cf-1-1')  # pylint: disable=no-member
    assert model.loan.get_meta('key') == 'cf-1-1'  # pylint: disable=no-member


def test_load_loan_with_meta():
    '''test load a simple model with json with some meta'''
    json_str = ('{"loan":{"@key":"cf-1-1","currency":"EUR","amount":"100"},'
                '"repayment":{"currency":"EUR","amount":"101"}}')
    model = DummyLoan2.model_validate_json(json_str)
    assert model.loan.get_meta('key') == 'cf-1-1'

# EOF
