'''test module for ref lifecycle'''
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


def test_ref_creation():
    '''no doc'''
    b = B(fieldB='some b content')
    a = A(b=b)
    root = Root(typeA=a, bAddress=Reference(a.b, 'aKey', KeyType.SCOPED))
    # pylint: disable=no-member
    assert id(root.typeA.b) == id(root.bAddress)


def test_deep_ref_creation():
    '''no doc'''
    b = B(fieldB='some b content')
    a = A(b=b)
    root = Root(typeA=a, bAddress=Reference(a.b, 'aKey2', KeyType.SCOPED))
    deep_ref = DeepRef(root=root)
    # pylint: disable=no-member
    assert id(deep_ref.root.typeA.b) == id(deep_ref.root.bAddress)


def test_fail_wrong_key_ext():
    '''no doc'''
    b = B(fieldB='some b content')
    a = A(b=b)
    with pytest.raises(ValueError):
        Root(typeA=a, bAddress=Reference(a.b, 'aKey', KeyType.EXTERNAL))


def test_fail_wrong_key_int():
    '''no doc'''
    b = B(fieldB='some b content')
    a = A(b=b)
    with pytest.raises(ValueError):
        Root(typeA=a, bAddress=Reference(a.b))

# EOF
