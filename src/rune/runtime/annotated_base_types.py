'''Classes representing annotated basic Rune types'''
from functools import partial
from decimal import Decimal
from pydantic import PlainSerializer, PlainValidator
from typing_extensions import Annotated


def _serialise_with_scheme(obj, base_type) -> dict:
    res = {'@data': base_type(obj)}
    if obj.scheme:
        res['@scheme'] = obj.scheme
    return res


def _deserialize_with_scheme(x, base_types, annotated_type):
    if isinstance(x, annotated_type):
        return x
    if isinstance(x, base_types):
        return annotated_type(x)
    scheme = x.get('@scheme')
    return annotated_type(x['@data'], scheme=scheme)


class AnnotatedString(str):
    '''annotated string'''
    def __new__(cls, value, scheme=None):
        obj = str.__new__(cls, value)
        obj.scheme = scheme
        return obj


class AnnotatedInt(int):
    '''annotated integer'''
    def __new__(cls, value, scheme=None):
        obj = int.__new__(cls, value)
        obj.scheme = scheme
        return obj


class AnnotatedNumber(Decimal):
    '''annotated number'''
    def __new__(cls, value, scheme=None):
        obj = Decimal.__new__(cls, value)
        obj.scheme = scheme
        return obj


_serialise_str_with_scheme = partial(_serialise_with_scheme, base_type=str)
_deserialize_str_with_scheme = partial(_deserialize_with_scheme,
                                       base_types=str,
                                       annotated_type=AnnotatedString)
_serialise_int_with_scheme = partial(_serialise_with_scheme, base_type=int)
_deserialize_int_with_scheme = partial(_deserialize_with_scheme,
                                       base_types=int,
                                       annotated_type=AnnotatedInt)
_serialise_number_with_scheme = partial(_serialise_with_scheme,
                                        base_type=Decimal)
_deserialize_number_with_scheme = partial(_deserialize_with_scheme,
                                          base_types=(Decimal, float, int, str),
                                          annotated_type=AnnotatedNumber)


AnnotatedStringProperty = Annotated[
    AnnotatedString,
    PlainSerializer(_serialise_str_with_scheme, return_type=dict),
    PlainValidator(_deserialize_str_with_scheme,
                   json_schema_input_type=str | dict)]

AnnotatedIntProperty = Annotated[
    AnnotatedInt,
    PlainSerializer(_serialise_int_with_scheme, return_type=dict),
    PlainValidator(_deserialize_int_with_scheme,
                   json_schema_input_type=int | str | dict)]

AnnotatedNumberProperty = Annotated[
    AnnotatedNumber,
    PlainSerializer(_serialise_number_with_scheme, return_type=dict),
    PlainValidator(_deserialize_number_with_scheme,
                   json_schema_input_type=float | int | str | dict)]

# EOF
