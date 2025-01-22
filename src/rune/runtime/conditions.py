'''facilities for rune conditions'''
from collections import defaultdict
from typing import Any

_CONDITIONS_REGISTRY: defaultdict[str, dict[str, Any]] = defaultdict(dict)


class ConditionViolationError(ValueError):
    '''Exception thrown on violation of a constraint'''


def rune_condition(condition):
    '''Wrapper to register all constraint functions in the global registry'''
    path_components = condition.__qualname__.split('.')
    path = '.'.join([condition.__module__ or ''] + path_components[:-1])
    name = path_components[-1]
    _CONDITIONS_REGISTRY[path][name] = condition

    return condition


def rune_local_condition(registry: dict):
    '''Registers a condition function in a local registry.'''

    def decorator(condition):
        path_components = condition.__qualname__.split('.')
        path = '.'.join([condition.__module__ or ''] + path_components)
        registry[path] = condition

        return condition

    return decorator


def rune_execute_local_conditions(registry: dict, cond_type: str):
    '''Executes all registered in a local registry.'''
    for condition_path, condition_func in registry.items():
        if not condition_func():
            raise ConditionViolationError(
                f"{cond_type} '{condition_path}' failed.")


def get_conditions(cls, base_class) -> list:
    '''returns the conditions registered for the passed in class'''
    res = []
    index = cls.__mro__.index(base_class)
    for c in reversed(cls.__mro__[:index]):
        fqcn = _fqcn(c)
        res += [('.'.join([fqcn, k]), v)
                for k, v in _CONDITIONS_REGISTRY.get(fqcn, {}).items()]
    return res


def _fqcn(cls) -> str:
    return '.'.join([cls.__module__ or '', cls.__qualname__])

# EOF
