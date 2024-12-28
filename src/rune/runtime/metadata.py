'''Classes representing annotated basic Rune types'''
from functools import partial, lru_cache
from decimal import Decimal
from typing import Any
from datetime import date, datetime, time
from pydantic import PlainSerializer, BeforeValidator, PlainValidator

META_CONTAINER = '__rune_metadata'


def _py_to_ser_key(key: str) -> str:
    if key[0] == '@':
        return key
    return '@' + key.replace('_', ':')


class BaseMetaDataMixin:
    '''Base class for the meta data support of basic amd complex types'''
    def init_meta(self, allowed_meta: set[str]):
        ''' if not initialised, just creates empty meta slots. If the metadata
            container is not empty, it will check if the already present keys
            are conform to the allowed keys.
        '''
        meta = self.__dict__.setdefault(META_CONTAINER, {})
        current_meta = set(meta.keys())
        if not current_meta.issubset(allowed_meta):
            raise ValueError(f'Allowed meta {allowed_meta} differs from the '
                             f'currently existing meta slots: {current_meta}')
        meta |= {k: None for k in allowed_meta - current_meta}

    def _get_meta_container(self) -> dict[str, Any]:
        return self.__dict__.get(META_CONTAINER, {})

    def _check_props_allowed(self, props: dict[str, Any]):
        if not props:
            return
        allowed = set(self._get_meta_container().keys())
        prop_keys = set(props.keys())
        if not prop_keys.issubset(allowed):
            raise ValueError('Not allowed metadata provided: '
                             f'{prop_keys - allowed}')

    def set_meta(self, check_allowed=True, **kwds):
        '''set some/all metadata properties'''
        props = {_py_to_ser_key(k): v for k, v in kwds.items()}
        if check_allowed:
            self._check_props_allowed(props)
        meta = self.__dict__.setdefault(META_CONTAINER, {})
        meta |= props

    def get_meta(self, name: str):
        '''get a metadata property'''
        return self._get_meta_container().get(_py_to_ser_key(name))

    def serialise_meta(self) -> dict:
        '''used as serialisation method with pydantic'''
        metadata = self._get_meta_container()
        return {key: value for key, value in metadata.items() if value}


class ComplexTypeMetaDataMixin(BaseMetaDataMixin):
    '''metadata support for complex types'''
    @classmethod
    def serialise(cls, obj) -> dict:
        '''used as serialisation method with pydantic'''
        res = obj.serialise_meta()
        res |= obj.model_dump(exclude_unset=True, exclude_defaults=True)
        return res

    @classmethod
    def deserialize(cls, obj, allowed_meta: set[str]):
        '''method used as pydantic `validator`'''
        if isinstance(obj, cls):
            obj.init_meta(allowed_meta)
            return obj

        metadata = {k: obj[k] for k in obj.keys() if k.startswith('@')}
        for k in metadata.keys():
            obj.pop(k)
        model = cls.model_validate(obj)  # type: ignore
        model.__dict__[META_CONTAINER] = metadata
        model.init_meta(allowed_meta)
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
    def serialise(cls, obj, base_type,) -> dict:
        '''used as serialisation method with pydantic'''
        res = obj.serialise_meta()
        res['@data'] = base_type(obj)
        return res

    @classmethod
    def deserialize(cls, obj, base_types, allowed_meta: set[str]):
        '''method used as pydantic `validator`'''
        if isinstance(obj, base_types) and not isinstance(obj, cls):
            obj = cls(obj)  # type: ignore
        elif isinstance(obj, dict):
            data = obj.pop('@data')
            obj = cls(data, **obj)  # type: ignore
        obj.init_meta(allowed_meta)
        return obj

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
        obj.set_meta(check_allowed=False, **kwds)
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
        obj.set_meta(check_allowed=False, **kwds)
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
        obj.set_meta(check_allowed=False, **kwds)
        return obj

    def __str__(self):
        return self.isoformat()


class StrWithMeta(str, BasicTypeMetaDataMixin):
    '''string with metadata'''
    def __new__(cls, value, **kwds):
        obj = str.__new__(cls, value)
        obj.set_meta(check_allowed=False, **kwds)
        return obj


class IntWithMeta(int, BasicTypeMetaDataMixin):
    '''annotated integer'''
    def __new__(cls, value, **kwds):
        obj = int.__new__(cls, value)
        obj.set_meta(check_allowed=False, **kwds)
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
        obj.set_meta(check_allowed=False, **kwds)
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
