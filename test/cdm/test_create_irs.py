'''create a test irs'''
# pylint: disable=invalid-name
import uuid
import os
from datetime import date
import pytest
from rune.runtime.base_data_class import BaseDataClass
try:
    # pylint: disable=unused-import
    # type: ignore
    from cdm.event.common.Trade import Trade
    from cdm.event.common.TradeIdentifier import TradeIdentifier
    from cdm.product.template.TradableProduct import TradableProduct
    from cdm.product.template.Product import Product
    from cdm.product.template.TradeLot import TradeLot
    from cdm.observable.asset.PriceQuantity import PriceQuantity
    from cdm.base.staticdata.party.Party import Party
    from cdm.base.staticdata.party.PartyIdentifier import PartyIdentifier
    from cdm.base.staticdata.party.Counterparty import Counterparty
    from cdm.base.staticdata.party.CounterpartyRoleEnum import CounterpartyRoleEnum
    # from cdm_observable_asset_Index import Index
    from cdm.base.staticdata.identifier.AssignedIdentifier import AssignedIdentifier
    from cdm.base.staticdata.party.PartyIdentifierTypeEnum import PartyIdentifierTypeEnum
    from cdm.event.common.TradeIdentifier import TradeIdentifier
    from cdm.base.staticdata.identifier.TradeIdentifierTypeEnum import TradeIdentifierTypeEnum
    from cdm.base.staticdata.identifier.AssignedIdentifier import AssignedIdentifier
    from cdm.product.template.Product import Product
    # from cdm.product.template.ContractualProduct import ContractualProduct
    from cdm.base.staticdata.asset.common.ProductTaxonomy import ProductTaxonomy
    from cdm.base.staticdata.asset.common.AssetClassEnum import AssetClassEnum
    from cdm.base.staticdata.asset.common.TaxonomySourceEnum import TaxonomySourceEnum
    from cdm.base.staticdata.asset.common.TaxonomyValue import TaxonomyValue
    from cdm.base.staticdata.asset.common.ProductIdentifier import ProductIdentifier
    from cdm.base.staticdata.asset.common.ProductIdTypeEnum import ProductIdTypeEnum
    from cdm.product.template.EconomicTerms import EconomicTerms
    from cdm.product.template.Payout import Payout
    from cdm.product.asset.InterestRatePayout import InterestRatePayout
    from cdm.base.staticdata.party.PayerReceiver import PayerReceiver
    from cdm.base.staticdata.party.CounterpartyRoleEnum import CounterpartyRoleEnum
    NO_SER_TEST_MOD = False
except ImportError:
    NO_SER_TEST_MOD = True


@pytest.mark.skipif(NO_SER_TEST_MOD, reason='CDM package not found')
def test_create_irs():
    '''minimal IRS trade'''
    party = [None, None]
    partyId = PartyIdentifier(identifier='54930084UKLVMY22DS16',
                              identifierType=PartyIdentifierTypeEnum.LEI)
    partyId.identifier.set_meta(  # pylint: disable=no-member
        scheme='http://www.fpml.org/coding-scheme/external/iso17442')
    party[0] = Party(partyId=[partyId], name='Party A')

    partyId1 = PartyIdentifier(identifier='851WYGNLUQLFZBSYGB56',
                              identifierType=PartyIdentifierTypeEnum.LEI)
    partyId1.identifier.set_meta(  # pylint: disable=no-member
        scheme='http://www.fpml.org/coding-scheme/external/iso17442')
    party[1] = Party(partyId=[partyId1], name='Party B')

    assignedIdentifier = AssignedIdentifier(identifier=str(uuid.uuid4()))
    assignedIdentifier.identifier.set_meta(  # pylint: disable=no-member
        scheme='http://www.fpml.org/coding-scheme/external/uti')
    tradeIdentifier = TradeIdentifier(
        issuer='54930084UKLVMY22DS16',
        assignedIdentifier=[assignedIdentifier],
        identifierType=TradeIdentifierTypeEnum.UNIQUE_TRANSACTION_IDENTIFIER)
    tradeIdentifier.issuer.set_meta(  # pylint: disable=no-member
        scheme='http://www.fpml.org/coding-scheme/external/iso17442')

    val = tradeIdentifier.rune_serialize()

    productTaxonomy = [None, None, None]
    productTaxonomy[0] = ProductTaxonomy(
        primaryAssetClass=AssetClassEnum.INTEREST_RATE)
    productTaxonomy[1] = ProductTaxonomy(
        source=TaxonomySourceEnum.ISDA,
        value=TaxonomyValue(name='InterestRate:IRSwap:FixedFloat'))
    productTaxonomy[2] = ProductTaxonomy(
        source=TaxonomySourceEnum.ISDA,
        productQualifier='InterestRate_IRSwap_FixedFloat')

    productIdentifier = ProductIdentifier(
        identifier='InterestRate:IRSwap:FixedFloat',
        source=ProductIdTypeEnum.OTHER)
    val = productIdentifier.rune_serialize()


    # priceQuantity = quantitySchedule

    # interestRatePayout = [None, None]
    # interestRatePayout[0] = InterestRatePayout(
    #     payerReceiver=PayerReceiver(payer=CounterpartyRoleEnum.PARTY_1,
    #                                 receiver=CounterpartyRoleEnum.PARTY_2))


    # payout = Payout()
    # economicTerms = EconomicTerms(payout=payout)

    # contractualProduct = ContractualProduct(
    #     productTaxonomy=productTaxonomy,
    #     productIdentifier=[productIdentifier],
    #     economicTerms=economicTerms)
    # val = contractualProduct.rune_serialize()

    # cdm_product_template_EconomicTerms
    #
    # product = Product()
    # tradableProduct = TradableProduct()

    # trade = Trade(tradeIdentifier=[tradeIdentifier],
    #               tradeDate=date.today().isoformat(),
    #               party=party,
    #               tradableProduct=tradableProduct)
    # val = trade.rune_serialize()
    assert val


@pytest.mark.skipif(NO_SER_TEST_MOD, reason='CDM package not found')
def test_rune_deserialize():
    '''no doc'''
    path = os.path.join(os.path.dirname(__file__), 'EUR-Vanilla-account.json')
    fp = open(path, 'rt', encoding='utf-8')
    obj = BaseDataClass.rune_deserialize(fp.read(), validate_model=False)
    assert obj

# EOF
