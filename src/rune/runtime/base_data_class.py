'''Base class for all Rune type classes'''
import logging
from typing import get_args, get_origin, Any
from pydantic import BaseModel, ValidationError, ConfigDict, model_serializer

from rune.runtime.conditions import ConditionViolationError
from rune.runtime.conditions import get_conditions
from rune.runtime.metadata import (ComplexTypeMetaDataMixin, Reference,
                                   REFS_CONTAINER, UnresolvedReference)


class BaseDataClass(BaseModel, ComplexTypeMetaDataMixin):
    ''' A base class for all cdm generated classes. It is derived from
        `pydantic.BaseModel` which provides type checking at object creation
        for all cdm classes. It provides as well the `validate_model`,
        `validate_conditions` and `validate_attribs` methods which perform the
        conditions, cardinality and type checks as specified in the rune
        type model. The method `validate_model` is not invoked automatically,
        but is left to the user to determine when to check the validity of the
        cdm model.
    '''
    model_config = ConfigDict(extra='ignore',
                              revalidate_instances='always',
                              arbitrary_types_allowed=True)

    def __setattr__(self, name: str, value: Any) -> None:
        if isinstance(value, Reference):
            self.bind_property_to(name, value)
        else:
            if name in self.__dict__.get(REFS_CONTAINER, {}):
                self.__dict__[REFS_CONTAINER].pop(name)
            super().__setattr__(name, value)

    @model_serializer(mode='wrap')
    def _resolve_refs(self, serializer, info):
        '''should replace objects with refs while serializing'''
        res = serializer(self, info)
        refs = self.__dict__.get(REFS_CONTAINER, {})
        for property_nm, (key, ref_type) in refs.items():
            res[property_nm] = {ref_type: key}
        return res

    def resolve_references(self):
        '''resolves all attributes which are references'''
        refs = []
        for prop_nm, obj in self.__dict__.items():
            if isinstance(obj, BaseDataClass):
                obj.resolve_references()
            elif isinstance(obj, UnresolvedReference):
                refs.append((prop_nm, obj.get_reference()))

        for prop_nm, ref in refs:
            self.bind_property_to(prop_nm, ref)

    def validate_model(self,
                       recursively: bool = True,
                       raise_exc: bool = True,
                       strict: bool = True) -> list:
        ''' This method performs full model validation. It will validate all
            attributes and it will also invoke `validate_conditions` to check
            all conditions and the cardinality of all attributes of this object.
            The parameter `raise_exc` controls whether an exception should be
            thrown if a validation or condition is violated or if a list with
            all encountered violations should be returned instead.
        '''
        try:
            self.disable_meta_checks()
            att_errors = self.validate_attribs(raise_exc=raise_exc,
                                               strict=strict)
            return att_errors + self.validate_conditions(
                recursively=recursively, raise_exc=raise_exc)
        finally:
            self.enable_meta_checks()

    def validate_attribs(self,
                         raise_exc: bool = True,
                         strict: bool = True) -> list:
        ''' This method performs attribute type validation.
            The parameter `raise_exc` controls whether an exception should be
            thrown if a validation or condition is violated or if a list with
            all encountered violations should be returned instead.
        '''
        try:
            self.model_validate(self, strict=strict)
        except ValidationError as validation_error:
            if raise_exc:
                raise validation_error
            return [validation_error]
        return []

    def validate_conditions(self,
                            recursively: bool = True,
                            raise_exc: bool = True) -> list:
        ''' This method will check all conditions and the cardinality of all
            attributes of this object. This includes conditions and cardinality
            of properties specified in the base classes. If the parameter
            `recursively` is set to `True`, it will invoke the validation on the
            rune defined attributes of this object too.
            The parameter `raise_exc` controls whether an exception should be
            thrown if a condition is not met or if a list with all encountered
            condition violations should be returned instead.
        '''
        self_rep = object.__repr__(self)
        logging.info('Checking conditions for %s ...', self_rep)
        exceptions = []
        for name, condition in get_conditions(self.__class__, BaseDataClass):
            logging.info('Checking condition %s for %s...', name, self_rep)
            if not condition(self):
                msg = f'Condition "{name}" for {repr(self)} failed!'
                logging.error(msg)
                exc = ConditionViolationError(msg)
                if raise_exc:
                    raise exc
                exceptions.append(exc)
            else:
                logging.info('Condition %s for %s satisfied.', name, self_rep)
        if recursively:
            for k, v in self.__dict__.items():
                logging.info('Validating conditions of property %s', k)
                exceptions += _validate_conditions_recursively(
                    v, raise_exc=raise_exc)
        err = f'with {len(exceptions)}' if exceptions else 'without'
        logging.info('Done conditions checking for %s %s errors.', self_rep,
                     err)
        return exceptions

    def check_one_of_constraint(self, *attr_names, necessity=True) -> bool:
        """ Checks that one and only one attribute is set. """
        values = self.model_dump()
        vals = [values.get(n) for n in attr_names]
        n_attr = sum(1 for v in vals if v is not None and v != [])
        if necessity and n_attr != 1:
            logging.error('One and only one of %s should be set!', attr_names)
            return False
        if not necessity and n_attr > 1:
            logging.error('Only one of %s can be set!', attr_names)
            return False
        return True

    def add_to_list_attribute(self, attr_name: str, value) -> None:
        """
        Adds a value to a list attribute, ensuring the value is of an allowed
        type.

        Parameters:
        attr_name (str): Name of the list attribute.
        value: Value to add to the list.

        Raises:
        AttributeError: If the attribute name is not found or not a list.
        TypeError: If the value type is not one of the allowed types.
        """
        if not hasattr(self, attr_name):
            raise AttributeError(f"Attribute {attr_name} not found.")

        attr = getattr(self, attr_name)
        if not isinstance(attr, list):
            raise AttributeError(f"Attribute {attr_name} is not a list.")

        # Get allowed types for the list elements
        allowed_types = self.get_allowed_types_for_list_field(attr_name)

        # Check if value is an instance of one of the allowed types
        if not isinstance(value, allowed_types):
            raise TypeError(f"Value must be an instance of {allowed_types}, "
                            f"not {type(value)}")

        attr.append(value)

    @classmethod
    def get_allowed_types_for_list_field(cls, field_name: str):
        """
        Gets the allowed types for a list field in a Pydantic model, supporting
        both Union and | operator.

        Parameters:
        cls (type): The Pydantic model class.
        field_name (str): The field name.

        Returns:
        tuple: A tuple of allowed types.
        """
        field_type = cls.__annotations__.get(field_name)
        if field_type and get_origin(field_type) is list:
            list_elem_type = get_args(field_type)[0]
            if get_origin(list_elem_type):
                return get_args(list_elem_type)
            return (list_elem_type, )  # Single type or | operator used
        return ()


def _validate_conditions_recursively(obj, raise_exc=True):
    '''Helper to execute conditions recursively on a model.'''
    if not obj:
        return []
    if isinstance(obj, BaseDataClass):
        return obj.validate_conditions(
            recursively=True,  # type:ignore
            raise_exc=raise_exc)
    if isinstance(obj, (list, tuple)):
        exc = []
        for item in obj:
            exc += _validate_conditions_recursively(item, raise_exc=raise_exc)
        return exc
    return []

# EOF
