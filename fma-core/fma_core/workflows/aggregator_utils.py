"""These functions are used to assist in the aggregator connector functionality."""
import abc
from typing import Any, Dict, Tuple


class AutoSubRegistrationMeta(abc.ABCMeta):
    """For registering subclasses."""

    def __new__(
        mcs, clsname: str, bases: Tuple[type, ...], attrs: Dict[str, object]
    ) -> Any:
        """Create auto registration object and return new class.

        :param clsname: Class name of the object that is being registered
        :type clsname: str
        :param bases: A tuple containing the base classes, in the order
            of their occurrence in the base class list.
        :type bases: Tuple[type, ...]
        :param attrs: Attributes used to create the object
        :type attrs: Dict[str, object]
        :return: A newly created class
        :rtype: Any
        """
        new_class: Any = super(AutoSubRegistrationMeta, mcs).__new__(
            mcs, clsname, bases, attrs
        )
        new_class._register_subclass()
        return new_class
