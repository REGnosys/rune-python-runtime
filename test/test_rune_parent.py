'''test module for rune root lifecycle'''
from typing import Optional, Annotated
from pydantic import Field
import pytest
from rune.runtime.metadata import Reference, KeyType
from rune.runtime.base_data_class import BaseDataClass


class B(BaseDataClass):
    '''no doc'''
    fieldB: str = Field(..., description='')


class A(BaseDataClass):
    '''no doc'''
    b: Annotated[B, B.serializer(),
                 B.validator(('@key:scoped', ))] = Field(..., description='')


class Root(BaseDataClass):
    '''no doc'''
    typeA: Optional[Annotated[A, A.serializer(),
                              A.validator()]] = Field(None, description='')
    bAddress: Optional[Annotated[B,
                                 B.serializer(),
                                 B.validator(('@ref:scoped', ))]] = Field(
                                     None, description='')
    _KEY_REF_CONSTRAINTS = {
        'bAddress': {'@ref:scoped'}
    }

class DeepRef(BaseDataClass):
    '''no doc'''
    root: Annotated[Root, Root.serializer(),
                    Root.validator()] = Field(..., description='')


def test_root_creation():
    '''no doc'''
    b = B(fieldB='some b content')
    a = A(b=b)
    root = Root(typeA=a, bAddress=Reference(a.b, 'aKey3', KeyType.SCOPED))
    # pylint: disable=no-member
    assert root.get_rune_parent() is None
    assert root == root.typeA.get_rune_parent()
    assert root.typeA == root.typeA.b.get_rune_parent()
    assert root.typeA == root.bAddress.get_rune_parent()
    assert root.typeA.b == root.bAddress


def test_deep_creation():
    '''no doc'''
    b = B(fieldB='some b content')
    a = A(b=b)
    root = Root(typeA=a, bAddress=Reference(a.b, 'aKey3', KeyType.SCOPED))
    deep = DeepRef(root=root)
    # pylint: disable=no-member
    assert deep.get_rune_parent() is None
    assert deep == deep.root.get_rune_parent()
    assert deep.root == deep.root.typeA.get_rune_parent()
    assert deep.root.typeA == deep.root.typeA.b.get_rune_parent()
    assert deep.root.typeA == deep.root.bAddress.get_rune_parent()
    assert deep.root.typeA.b == deep.root.bAddress


def test_root_deserialization():
    '''no doc'''
    rune_dict = {
        "typeA": {
            "b": {
                "@key:scoped": "aKey3",
                "fieldB": "some b content"
            }
        },
        "bAddress": {
            "@ref:scoped": "aKey3"
        }
    }
    root = Root.model_validate(rune_dict)
    assert root.get_rune_parent() is None
    assert root == root.typeA.get_rune_parent()
    assert root.typeA == root.typeA.b.get_rune_parent()
    assert root.typeA == root.bAddress.get_rune_parent()
    assert root.typeA.b == root.bAddress


def test_deep_deserialization():
    '''no doc'''
    rune_dict = {
        "root": {
            "typeA": {
                "b": {
                    "@key:scoped": "aKey3",
                    "fieldB": "some b content"
                }
            },
            "bAddress": {
                "@ref:scoped": "aKey3"
            }
        }
    }
    deep = DeepRef.model_validate(rune_dict)
    assert deep.get_rune_parent() is None
    assert deep == deep.root.get_rune_parent()
    assert deep.root == deep.root.typeA.get_rune_parent()
    assert deep.root.typeA == deep.root.typeA.b.get_rune_parent()
    assert deep.root.typeA == deep.root.bAddress.get_rune_parent()
    assert deep.root.typeA.b == deep.root.bAddress

# EOF
