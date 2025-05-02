'''functions to work with the global object registry'''

_OBJECT_REGISTRY: dict[str, tuple[object, str]] = {}


def get_object(key: str) -> tuple[object, str]:
    '''retrieve an object, if not found, an exception will be thrown'''
    return _OBJECT_REGISTRY[key]


def register_object(obj: tuple[object, str], key: str):
    '''register and object in the global registry'''
    if key in _OBJECT_REGISTRY:
        raise ValueError(f"Key {key} already exists! Can't register {obj}!")
    _OBJECT_REGISTRY[key] = obj

# EOD
