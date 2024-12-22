'''Classes representing annotated basic Rune types'''
from functools import partial, lru_cache
from decimal import Decimal
from datetime import date, datetime, time
from pydantic import PlainSerializer, BeforeValidator

META_CONTAINER = '__rune_metadata'


def _py_to_ser_key(key: str) -> str:
    if key[0] == '@':
        return key
    return '@' + key.replace('_', ':')


class BaseMetaDataMixin:
    '''Base class for the meta data support of basic amd complex types'''
    _metadata_keys = {
        '@scheme', '@key', '@ref', '@key:external', '@ref:external',
        '@key:scoped', '@ref:scoped'
    }

    @classmethod
    def _check_allowed(cls, metadata: dict, allowed_meta: set[str]):
        keys = set(metadata.keys())
        if not keys.issubset(allowed_meta):
            raise ValueError('Not allowed metadata provided: '
                             f'{keys - allowed_meta}')

    def set_meta(self, **kwds):
        '''set some/all metadata properties'''
        props = {_py_to_ser_key(k): v for k, v in kwds.items()}
        self._check_allowed(props, self._metadata_keys)
        meta = self.__dict__.setdefault(META_CONTAINER, {})
        meta |= props

    def get_meta(self, name: str):
        '''get a metadata property'''
        return self.__dict__.get(META_CONTAINER, {}).get(_py_to_ser_key(name))


class BasicTypeMetaDataMixin(BaseMetaDataMixin):
    '''holds the metadata associated with an instance'''

    @classmethod
    def serialise(cls,
                  obj,
                  base_type,
                  allowed_meta: set[str] | None = None) -> dict:
        '''used as serialisation method with pydantic'''
        allowed_meta = allowed_meta or cls._metadata_keys
        metadata = obj.__dict__.get(META_CONTAINER, {})
        res = {key: value for key, value in metadata.items() if value}
        cls._check_allowed(metadata, allowed_meta)
        res['@data'] = base_type(obj)
        return res

    @classmethod
    def deserialize(cls, obj, base_types, meta_type, allowed_meta: set[str]):
        '''method used as pydantic `validator`'''
        if isinstance(obj, meta_type):
            metadata = obj.__dict__.get(META_CONTAINER, {})
            cls._check_allowed(metadata, allowed_meta)
            return obj
        if isinstance(obj, base_types):
            return meta_type(obj)

        #FIXME: assuming dict - shall we check?
        data = obj.pop('@data')
        cls._check_allowed(obj, allowed_meta)
        return meta_type(data, **obj)

    @classmethod
    @lru_cache
    def serializer(cls):
        '''should return the validator for the specific class'''
        ser_fn = partial(cls.serialise, base_type=str)
        return PlainSerializer(ser_fn, return_type=dict)

    @classmethod
    @lru_cache
    def validator(cls, allowed_meta: tuple[str]):
        '''default validator for the specific class'''
        allowed = set(allowed_meta)
        return BeforeValidator(partial(cls.deserialize,
                                       base_types=str,
                                       meta_type=cls,
                                       allowed_meta=allowed),
                               json_schema_input_type=str | dict)


class DateWithMeta(date, BasicTypeMetaDataMixin):
    '''date with metadata'''
    def __new__(cls, value, **kwds):  # pylint: disable=signature-differs
        ymd = date.fromisoformat(value).timetuple()[:3]
        obj = date.__new__(cls, *ymd)
        obj.set_meta(**{_py_to_ser_key(k): v for k, v in kwds.items()})
        return obj


class TimeWithMeta(time, BasicTypeMetaDataMixin):
    '''annotated time'''
    def __new__(cls, value, **kwds):  # pylint: disable=signature-differs
        aux = time.fromisoformat(value)
        obj = time.__new__(cls,
                           aux.hour,
                           aux.minute,
                           aux.second,
                           aux.microsecond,
                           aux.tzinfo,
                           fold=aux.fold)
        obj.set_meta(**{_py_to_ser_key(k): v for k, v in kwds.items()})
        return obj


class DateTimeWithMeta(datetime, BasicTypeMetaDataMixin):
    '''annotated datetime'''
    def __new__(cls, value, **kwds):  # pylint: disable=signature-differs
        aux = datetime.fromisoformat(value)
        obj = datetime.__new__(cls,
                               aux.year,
                               aux.month,
                               aux.day,
                               aux.hour,
                               aux.minute,
                               aux.second,
                               aux.microsecond,
                               aux.tzinfo,
                               fold=aux.fold)
        obj.set_meta(**{_py_to_ser_key(k): v for k, v in kwds.items()})
        return obj

    def __str__(self):
        return self.isoformat()


class StrWithMeta(str, BasicTypeMetaDataMixin):
    '''string with metadata'''
    def __new__(cls, value, **kwds):
        obj = str.__new__(cls, value)
        obj.set_meta(**{_py_to_ser_key(k): v for k, v in kwds.items()})
        return obj


class IntWithMeta(int, BasicTypeMetaDataMixin):
    '''annotated integer'''
    def __new__(cls, value, **kwds):
        obj = int.__new__(cls, value)
        obj.set_meta(**{_py_to_ser_key(k): v for k, v in kwds.items()})
        return obj

    @classmethod
    @lru_cache
    def serializer(cls):
        '''should return the validator for the specific class'''
        ser_fn = partial(cls.serialise, base_type=int)
        return PlainSerializer(ser_fn, return_type=dict)

    @classmethod
    @lru_cache
    def validator(cls, allowed_meta: tuple[str]):
        '''default validator for the specific class'''
        allowed = set(allowed_meta)
        return BeforeValidator(partial(cls.deserialize,
                                       base_types=int,
                                       meta_type=cls,
                                       allowed_meta=allowed),
                               json_schema_input_type=int | dict)


class NumberWithMeta(Decimal, BasicTypeMetaDataMixin):
    '''annotated number'''
    def __new__(cls, value, **kwds):
        obj = Decimal.__new__(cls, value)
        obj.set_meta(**{_py_to_ser_key(k): v for k, v in kwds.items()})
        return obj

    @classmethod
    @lru_cache
    def serializer(cls):
        '''should return the validator for the specific class'''
        ser_fn = partial(cls.serialise, base_type=Decimal)
        return PlainSerializer(ser_fn, return_type=dict)

    @classmethod
    @lru_cache
    def validator(cls, allowed_meta: tuple[str]):
        '''default validator for the specific class'''
        allowed = set(allowed_meta)
        return BeforeValidator(partial(cls.deserialize,
                                       base_types=(Decimal, float, int, str),
                                       meta_type=cls,
                                       allowed_meta=allowed),
                               json_schema_input_type=float | int | str | dict)


# _serialise_str_with_scheme = partial(_serialise_with_scheme, base_type=str)
# _deserialize_str_with_scheme = partial(_deserialize_with_scheme,
#                                        base_types=str,
#                                        annotated_type=AnnotatedString)

# _serialise_int_with_scheme = partial(_serialise_with_scheme, base_type=int)
# _deserialize_int_with_scheme = partial(_deserialize_with_scheme,
#                                        base_types=int,
#                                        annotated_type=AnnotatedInt)

# _serialise_number_with_scheme = partial(_serialise_with_scheme,
#                                         base_type=Decimal)
# _deserialize_number_with_scheme = partial(_deserialize_with_scheme,
#                                           base_types=(Decimal, float, int, str),
#                                           annotated_type=AnnotatedNumber)

# _serialise_date_with_scheme = partial(_serialise_with_scheme, base_type=str)
# _deserialize_date_with_scheme = partial(_deserialize_with_scheme,
#                                         base_types=str,
#                                         annotated_type=AnnotatedDate)

# _serialise_datetime_with_scheme = partial(_serialise_with_scheme, base_type=str)
# _deserialize_datetime_with_scheme = partial(_deserialize_with_scheme,
#                                             base_types=str,
#                                             annotated_type=AnnotatedDateTime)

# _serialise_time_with_scheme = partial(_serialise_with_scheme, base_type=str)
# _deserialize_time_with_scheme = partial(_deserialize_with_scheme,
#                                         base_types=str,
#                                         annotated_type=AnnotatedTime)


# AnnotatedStringProperty = Annotated[
#     AnnotatedString,
#     PlainSerializer(_serialise_str_with_scheme, return_type=dict),
#     PlainValidator(_deserialize_str_with_scheme,
#                    json_schema_input_type=str | dict)]

# AnnotatedIntProperty = Annotated[
#     AnnotatedInt,
#     PlainSerializer(_serialise_int_with_scheme, return_type=dict),
#     PlainValidator(_deserialize_int_with_scheme,
#                    json_schema_input_type=int | str | dict)]

# AnnotatedNumberProperty = Annotated[
#     AnnotatedNumber,
#     PlainSerializer(_serialise_number_with_scheme, return_type=dict),
#     PlainValidator(_deserialize_number_with_scheme,
#                    json_schema_input_type=float | int | str | dict)]

# AnnotatedDateProperty = Annotated[
#     AnnotatedDate,
#     PlainSerializer(_serialise_date_with_scheme, return_type=dict),
#     PlainValidator(_deserialize_date_with_scheme,
#                    json_schema_input_type=str | dict)]

# AnnotatedDateTimeProperty = Annotated[
#     AnnotatedDate,
#     PlainSerializer(_serialise_datetime_with_scheme, return_type=dict),
#     PlainValidator(_deserialize_datetime_with_scheme,
#                    json_schema_input_type=str | dict)]

# AnnotatedTimeProperty = Annotated[
#     AnnotatedDate,
#     PlainSerializer(_serialise_time_with_scheme, return_type=dict),
#     PlainValidator(_deserialize_time_with_scheme,
#                    json_schema_input_type=str | dict)]

# EOF
