# -*- coding: UTF-8 -*-
# Copyright 2010-2013 Felix Schwarz
# The source code in this file is licensed under the MIT license.

import inspect

__all__ = ["attrs", "BaseConstantsClass"]


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


class ConstantValueBuilder(type):
    
    def __new__(cls, classname, direct_superclasses, class_attributes_dict):
        constants = cls._constants(class_attributes_dict)
        constants_map = cls._add_class_attributes_for_simple_access(class_attributes_dict, constants)
        class_attributes_dict['_constants_map'] = constants_map
        constants_class = cls.instantiate(classname, direct_superclasses, class_attributes_dict)
        
        constants_class._constants = cls.declaration_order_of_constants(constants_class)
        return constants_class
    
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
            if callable(value) or not isinstance(value, (basestring, int, tuple)):
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
    def declaration_order_of_constants(cls, constants_class):
        # workaround to preserve the order of attribute declaration
        # see attrs.__init__()
        constants_map = constants_class._constants_map
        class_members = inspect.getmembers(constants_class)
        unsorted_members = filter(lambda member: (member[0] in constants_map), class_members)
        unsorted_names = [member[0] for member in unsorted_members]
        
        if '_' in constants_map:
            optional_value = constants_map['_']
            del constants_map['_']
            constants_map[None] = optional_value
            
            for i, name in enumerate(unsorted_names):
                if name == '_':
                    unsorted_names[i] = None
                    break
        
        sorted_names = sorted(unsorted_names, key=lambda name: constants_map[name]._order)
        return tuple(sorted_names)


class NotSet(object):
    pass


class BaseConstantsClass(object):
    
    __metaclass__ = ConstantValueBuilder
    
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

