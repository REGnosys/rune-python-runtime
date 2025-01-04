'''functions to work with the global object registry'''

_OBJECT_REGISTRY: dict[str, object] = {}


def get_object(key: str) -> object:
    '''retrieve an object, if not found, None will be returned'''
    return _OBJECT_REGISTRY.get(key)


def register_object(obj: object, key: str):
    '''register and object in the global registry'''
    if key in _OBJECT_REGISTRY:
        raise ValueError(f"Key {key} already exists! Can't register {obj}!")
    _OBJECT_REGISTRY[key] = obj

# EOD
