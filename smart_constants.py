# -*- coding: UTF-8 -*-
# Copyright 2010-2015, 2017 Felix Schwarz
# The source code in this file is licensed under the MIT license.

from collections import namedtuple
import inspect

import six

__all__ = ["attrs", "BaseConstantsClass"]


def sort_by_list(values, id_list, key_callable):
    """Sort values according to a custom list of ids.

    @param values:       list of values for sorting
    @param id_list:      list of ids which will determine the sort order
    @param key_callable: callable which (given a value) returns <id of value>
    @return: sorted values
    """
    SortableResult = namedtuple('SortableResult', 'item id')
    sortable_results = [SortableResult(option, key_callable(option)) for option in values]
    # if an id occurs later in id_list its index will be higher so Python's
    # sorted() will place the item after the ones with a lower index.
    sorted_tuples = sorted(sortable_results, key=lambda item: id_list.index(item.id))
    sorted_results = tuple([sort_result.item for sort_result in sorted_tuples])
    return sorted_results


class attrs(object):
    counter = 0
    
    def __init__(self, label=None, visible=True, value=None, data=None):
        self.label = label
        self.visible = visible
        self.value = value
        self.data = data
        
        # declaration of attributes should affect ordering of items later on
        # (e.g. in a select widget). In Python 2 we have to use some workarounds
        # to make that happen.
        # http://stackoverflow.com/questions/4459531/how-to-read-class-attributes-in-the-same-order-as-declared
        self._order = attrs.counter
        attrs.counter += 1
    
    def __repr__(self):
        classname = self.__class__.__name__
        parameters = (classname, self.label, self.visible, self.value, self.data, self._order)
        return '%s(label=%r, visible=%r, value=%r, data=%r, _order=%r)' % parameters


class record_attribute_order(dict):
    def __init__(self):
       self.ordered_attribute_names = []

    def __setitem__(self, key, value):
       if key not in self:
          self.ordered_attribute_names.append(key)
       dict.__setitem__(self, key, value)


class ConstantValueBuilder(type):
    
    def __new__(cls, classname, direct_superclasses, class_attributes_dict):
        constants = cls._constants(class_attributes_dict)
        constants_map = cls._add_class_attributes_for_simple_access(class_attributes_dict, constants)
        class_attributes_dict['_constants_map'] = constants_map
        constants_class = cls.instantiate(classname, direct_superclasses, class_attributes_dict)

        constants_class._constants = cls.declaration_order_of_constants(constants_class, class_attributes_dict)
        return constants_class

    # only called when using Python 3
    @classmethod
    def __prepare__(metacls, name, bases):
        return record_attribute_order()

    @classmethod
    def instantiate(cls, classname, direct_superclasses, class_attributes_dict):
        return type.__new__(cls, classname, direct_superclasses, class_attributes_dict)
    
    @classmethod
    def _constants(cls, attributes):
        constants = []
        for name in attributes:
            # '_' means 'empty value' (because we can't assign to None)
            # need that but other private attributes should be ignored
            if name.startswith('_') and name != '_':
                continue
            value = attributes[name]
            if callable(value) or not isinstance(value, six.string_types + (int, tuple)):
                continue
            constants.append((name, value))
        return constants
    
    @classmethod
    def _add_class_attributes_for_simple_access(cls, attributes, constants):
        constants_map = dict()
        for name, value in constants:
            if isinstance(value, tuple):
                assert len(value) == 2
                attribute = value[1]
                attribute.value = value[0]
            elif name == '_':
                attribute = attrs(value=None, label=value)
            else:
                attribute = attrs(value=value, label=value)
            attributes[name] = attribute.value
            constants_map[name] = attribute
        return constants_map
    
    @classmethod
    def declaration_order_of_constants(cls, constants_class, class_attributes_dict):
        # Python 2 needs a workaround (aka "hack") to preserve the order of
        # attribute declaration (see attrs.__init__()).
        # Python 3 provides more hooks (PEP 3115) so we achieve our goal there
        # without tricks.
        constants_map = constants_class._constants_map
        class_members = inspect.getmembers(constants_class)
        unsorted_members = filter(lambda member: (member[0] in constants_map), class_members)
        unsorted_names = [member[0] for member in unsorted_members]
        
        if '_' in constants_map:
            optional_value = constants_map.pop('_')
            constants_map[None] = optional_value
            
            for i, name in enumerate(unsorted_names):
                if name == '_':
                    unsorted_names[i] = None
                    break

        if six.PY3:
            ordered_attributes = class_attributes_dict.ordered_attribute_names
            replaced_optional = [(name if name != '_' else None) for name in ordered_attributes]
            sorted_names = sort_by_list(unsorted_names, replaced_optional, lambda name: name)
        else:
            sorted_names = sorted(unsorted_names, key=lambda name: constants_map[name]._order)
        return tuple(sorted_names)


class NotSet(object):
    pass


class BaseConstantsClass(six.with_metaclass(ConstantValueBuilder, object)):
    
    @classmethod
    def constants(cls):
        """Gibt die String-Namen zurück, die auf Python-Seite verwendet werden."""
        return cls._constants
    
    
    @classmethod
    def values(cls):
        """Gibt die Werte der Konstanten zurück (z.B. int), die extern 
        (z.B. Datenbank, XML) verwendet werden."""
        _values = [cls._constants_map[key].value for key in cls._constants]
        return tuple(_values)
    
    
    @classmethod
    def constant_for(cls, a_value, not_found_message=None):
        for key, attributes in cls._constants_map.items():
            if attributes.value == a_value:
                return key
        if not_found_message is not None:
            raise AssertionError(not_found_message)
        raise AssertionError("No constant found for %s" % repr(a_value))
    
    
    @classmethod
    def label_for(cls, a_value):
        constant = cls.constant_for(a_value)
        attributes = cls._constants_map[constant]
        return attributes.label
    
    
    @classmethod
    def data_for(cls, a_value):
        constant = cls.constant_for(a_value)
        attributes = cls._constants_map[constant]
        return attributes.data
    
    
    @classmethod
    def options(cls, current_value=NotSet):
        """Gibt eine Liste von Tupeln (value, label) zurück, die für 
        Select-Felder genutzt werden können."""
        _options = []
        for key in cls._constants:
            attr = cls._constants_map[key]
            if (not attr.visible) and (not attr.value == current_value):
                continue
            _options.append((attr.value, attr.label))
        return tuple(_options)

    @classmethod
    def as_enum(cls):
        enum_options = dict()
        for key, constant in cls._constants_map.items():
            enum_options[key] = constant.value
        # enum was added in Python 3.4 (backport 'enum34' available for
        # Python 2.6-3.4)
        # If enum is not available just fail with an ImportError.
        from enum import Enum
        enum_instance = Enum(cls.__name__, enum_options)
        return enum_instance

