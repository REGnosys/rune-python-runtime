'''
Testing the following Rune definitions:

type A:
    [metadata key]
    fieldA string (1..1)

type NodeRef:
    typeA A (0..1)
    aReference A (0..1)
        [metadata reference]

type AttributeRef:
    dateField date (0..1)
        [metadata id]
    dateReference date (0..1)
        [metadata reference]

type Root:
    [rootType]
    nodeRef NodeRef (0..1)
    attributeRef AttributeRef (0..1)
'''
import datetime
from typing_extensions import Annotated, Optional
import pytest
from pydantic import Field
from rune.runtime.base_data_class import BaseDataClass
from rune.runtime.metadata import DateWithMeta


class A(BaseDataClass):
    '''no doc'''
    fieldA: str = Field(..., description="")  # type: ignore


class NodeRef(BaseDataClass):
    '''no doc'''
    # NOTE: the @key is generated for all instances of A as it is annotated
    # in the type definition with key!!
    typeA: Optional[Annotated[
        A,  # type: ignore
        A.serializer(),
        A.validator(('@key', ))]] = Field(None, description='')
    # NOTE: the @key is generated for all instances of A as it is annotated
    # in the type definition with key!!
    aReference: Optional[Annotated[
        A,  # type: ignore
        A.serializer(),
        A.validator(('@key', '@ref'))]] = Field(None, description='')

    _KEY_REF_CONSTRAINTS = {
        'aReference': {'@ref', '@ref:external'}
    }

class AttributeRef(BaseDataClass):
    '''no doc'''
    # type: ignore
    dateField: Optional[Annotated[  # type: ignore
        DateWithMeta,
        DateWithMeta.serializer(),
        DateWithMeta.validator(('@key', ))]] = Field(None, description='')
    dateReference: Optional[Annotated[  # type: ignore
        DateWithMeta,
        DateWithMeta.serializer(),
        DateWithMeta.validator(('@ref', ))]] = Field(None, description='')

    _KEY_REF_CONSTRAINTS = {
        'dateReference': {'@ref', '@ref:external'}
    }


class Root(BaseDataClass):
    '''no doc'''
    # type: ignore
    nodeRef: Optional[NodeRef] = Field(None, description='')  # type: ignore
    attributeRef: Optional[AttributeRef] = Field(  # type: ignore
        None, description='')


def test_attribute_ref():
    '''attribute-ref.json'''
    json_str = '''
        {
            "attributeRef" : {
                "dateField" : {
                    "@data" : "2024-12-12",
                    "@key" : "someKey"
                },
                "dateReference" : {
                    "@ref" : "someKey"
                }
            }
        }
    '''
    model = Root.model_validate_json(json_str)
    model.resolve_references()
    model.validate_model()
    assert model.attributeRef.dateField == datetime.date(2024, 12, 12)
    assert model.attributeRef.dateReference == datetime.date(2024, 12, 12)
    assert (id(model.attributeRef.dateField) == id(
        model.attributeRef.dateReference))


def test_node_ref():
    '''node-ref.json'''
    json_str = '''
        {
            "nodeRef" : {
                "typeA" : {
                    "fieldA" : "foo",
                    "@key" : "someKey1"
                },
                "aReference" : {
                    "@ref" : "someKey1"
                }
            }
        }
    '''
    model = Root.model_validate_json(json_str)
    model.resolve_references()
    model.validate_model()
    assert model.nodeRef.typeA.fieldA == 'foo'
    assert model.nodeRef.aReference.fieldA == 'foo'
    assert id(model.nodeRef.typeA.fieldA) == id(model.nodeRef.aReference.fieldA)


def test_dangling_attribute_ref():
    '''dangling-attribute-ref.json'''
    json_str = '''
        {
            "attributeRef" : {
                "dateReference" : {
                    "@ref" : "someKey2"
                }
            }
        }
    '''
    with pytest.raises(KeyError):
        Root.model_validate_json(json_str)


def test_dangling_node_ref():
    '''dangling-node-ref.json'''
    json_str = '''
        {
            "nodeRef" : {
                "aReference" : {
                    "@ref" : "someKey3"
                }
            }
        }
    '''
    with pytest.raises(KeyError):
        Root.model_validate_json(json_str)

# EOF
