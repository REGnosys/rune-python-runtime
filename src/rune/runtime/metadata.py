'''Classes representing annotated basic Rune types'''
from functools import partial, lru_cache
from decimal import Decimal
from datetime import date, datetime, time
from pydantic import PlainSerializer, BeforeValidator, PlainValidator

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
        if not metadata:
            return
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

    @classmethod
    def serialise_meta(cls, obj, allowed_meta: set[str] | None = None) -> dict:
        '''used as serialisation method with pydantic'''
        allowed_meta = allowed_meta or cls._metadata_keys
        metadata = obj.__dict__.get(META_CONTAINER, {})
        res = {key: value for key, value in metadata.items() if value}
        cls._check_allowed(metadata, allowed_meta)
        return res


class ComplexTypeMetaDataMixin(BaseMetaDataMixin):
    '''metadata support for complex types'''
    @classmethod
    def serialise(cls,
                  obj,
                  allowed_meta: set[str] | None = None) -> dict:
        '''used as serialisation method with pydantic'''
        res = cls.serialise_meta(obj, allowed_meta)
        res |= obj.model_dump(exclude_unset=True, exclude_defaults=True)
        return res

    @classmethod
    def deserialize(cls, obj, allowed_meta: set[str]):
        '''method used as pydantic `validator`'''
        if isinstance(obj, cls):
            metadata = obj.__dict__.get(META_CONTAINER, {})
            cls._check_allowed(metadata, allowed_meta)
            return obj

        metadata = {k: obj[k] for k in obj.keys() if k.startswith('@')}
        for k in metadata.keys():
            obj.pop(k)
        cls._check_allowed(metadata, allowed_meta)
        model = cls.model_validate(obj)  # type: ignore
        model.__dict__[META_CONTAINER] = metadata
        return model

    @classmethod
    @lru_cache
    def serializer(cls):
        '''should return the validator for the specific class'''
        return PlainSerializer(cls.serialise, return_type=dict)

    @classmethod
    @lru_cache
    def validator(cls, allowed_meta: tuple[str]):
        '''default validator for the specific class'''
        allowed = set(allowed_meta)
        return PlainValidator(partial(cls.deserialize, allowed_meta=allowed),
                              json_schema_input_type=dict)


class BasicTypeMetaDataMixin(BaseMetaDataMixin):
    '''holds the metadata associated with an instance'''

    @classmethod
    def serialise(cls,
                  obj,
                  base_type,
                  allowed_meta: set[str] | None = None) -> dict:
        '''used as serialisation method with pydantic'''
        res = cls.serialise_meta(obj, allowed_meta)
        res['@data'] = base_type(obj)
        return res

    @classmethod
    def deserialize(cls, obj, base_types, allowed_meta: set[str]):
        '''method used as pydantic `validator`'''
        if isinstance(obj, cls):
            metadata = obj.__dict__.get(META_CONTAINER, {})
            cls._check_allowed(metadata, allowed_meta)
            return obj
        if isinstance(obj, base_types):
            return cls(obj)  # type: ignore

        #FIXME: assuming dict - shall we check?
        data = obj.pop('@data')
        cls._check_allowed(obj, allowed_meta)
        return cls(data, **obj)  # type: ignore

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
                                       allowed_meta=allowed),
                               json_schema_input_type=float | int | str | dict)

# EOF
