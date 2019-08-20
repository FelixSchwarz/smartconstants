# -*- coding: UTF-8 -*-
# Copyright 2010-2013, 2017 Felix Schwarz
# The source code in this file is licensed under the MIT license.

from __future__ import absolute_import, print_function, unicode_literals

from pythonic_testcase import *

from smart_constants import attrs, BaseConstantsClass


class DummyConstants(BaseConstantsClass):
    foo = "bar"
    bar = "quux"
    
    _fnord = "fnord"
    
    def fnord(self):
        return None

def skip_unless_enum_is_available():
    try:
        import enum
        has_enum = True
    except ImportError:
        has_enum = False
    if not has_enum:
        skip_test('no enum module available')


class BaseConstantsClassTest(PythonicTestCase):
    def test_ignores_private_names(self):
        assert_not_contains("_fnord", DummyConstants.constants())
    
    def test_ignores_functions(self):
        assert_not_contains("fnord", DummyConstants.constants())
    
    def test_can_get_names_of_all_defined_constants(self):
        assert_equals(("foo", "bar"), DummyConstants.constants())
    
    def test_can_get_values_of_all_defined_constants(self):
        assert_equals(("bar", "quux"), DummyConstants.values())
    
    def test_can_return_name_for_specified_value(self):
        assert_equals("bar", DummyConstants.constant_for("quux"))

    def test_can_return_enum_instance(self):
        skip_unless_enum_is_available()
        dummy_enum = DummyConstants.as_enum()
        assert_equals('bar', dummy_enum.foo.value)
        assert_equals('quux', dummy_enum.bar.value)
        assert_false(hasattr(dummy_enum, '_fnord'))

        dummy_enum2 = DummyConstants.as_enum()
        assert_equals(
            id(dummy_enum), id(dummy_enum2),
            message='returned enum instance should be a singleton'
        )

    def test_provides_enum_methods(self):
        skip_unless_enum_is_available()
        assert_true(hasattr(DummyConstants, '__members__'))
        dummy_enum = DummyConstants.as_enum()
        assert_equals(dummy_enum.__members__, DummyConstants.__members__)


class CodesWithAttributes(BaseConstantsClass):
    foo = 4, attrs(label="Foo")
    bar = 5, attrs(label="Bar")
    qux = 2, attrs(label="Quux")


class CodesWithHiddenAttributes(BaseConstantsClass):
    foo = 4, attrs(label="Foo", visible=False)
    bar = 5, attrs(label="Bar", visible=True)

class MethodAutoGenerationForBaseConstantsTest(PythonicTestCase):
    def test_can_get_values_even_with_extended_attributes(self):
        assert_equals((4, 5, 2), CodesWithAttributes.values())
    
    def test_can_access_constants_as_attributes(self):
        assert_equals(4, CodesWithAttributes.foo)
    
    def test_can_get_constant_names_even_with_extended_attributes(self):
        assert_equals(("foo", "bar", "qux"), CodesWithAttributes.constants())
    
    def test_can_return_options_for_select(self):
        assert_equals(((4, "Foo"), (5, "Bar"), (2, "Quux")), 
                      CodesWithAttributes.options())
    
    def test_hidden_constants_are_not_returned_for_select(self):
        assert_equals(((5, "Bar"),), CodesWithHiddenAttributes.options())
    
    def test_can_return_hidden_constant_if_it_is_the_current_value(self):
        """Sometimes it is desirable to allow certain values in a select field
        even if the constant is usually hidden. For example some constants
        should be phased out but existing data should be editable without the
        need to change the current value."""
        assert_equals(((5, "Bar"),), CodesWithHiddenAttributes.options())
        
        options = CodesWithHiddenAttributes.options(current_value=CodesWithHiddenAttributes.foo)
        assert_equals(((4, "Foo"), (5, "Bar")), options)
    
    def test_can_get_label_for_value(self):
        assert_equals("Foo", CodesWithAttributes.label_for(CodesWithAttributes.foo))
        assert_equals("Quux", CodesWithAttributes.label_for(CodesWithAttributes.qux))
    
    def test_uses_value_as_label_for_simple_constants(self):
        assert_equals("quux", DummyConstants.label_for(DummyConstants.bar))


class ConstantWithEmptyValueTest(PythonicTestCase):
    def test_can_define_optional_value_with_string_label(self):
        class OptionalCode(BaseConstantsClass):
            _ = 'empty'
            foo = 4, attrs(label="Foo")
        
        # the optional value does not use an attrs object, therefore ordering
        # of constants is undefined (=> use a set for assertions)
        assert_equals(set((None, 'foo')), set(OptionalCode.constants()))
        assert_equals(set((None, 4)), set(OptionalCode.values()))
        assert_equals(set(((None, 'empty'), (4, 'Foo'))), 
                      set(OptionalCode.options()))
    
    def test_can_define_optional_value_with_attrs(self):
        class OptionalCode(BaseConstantsClass):
            _ = None, attrs(label='empty')
            foo = 4, attrs(label="Foo")
        assert_equals((None, 'foo'), OptionalCode.constants())
        assert_equals((None, 4), OptionalCode.values())
        assert_equals(((None, 'empty'), (4, 'Foo')), OptionalCode.options())
    
    def test_can_define_hidden_optional_value(self):
        class OptionalCode(BaseConstantsClass):
            _ = None, attrs(visible=False)
            foo = 4, attrs(label="Foo")
        assert_equals(((4, 'Foo'),), OptionalCode.options())
        assert_equals(((None, None), (4, 'Foo')), 
                      OptionalCode.options(current_value=None))


class ConstantWithCustomDataTest(PythonicTestCase):
    def test_can_add_custom_data(self):
        class OptionalData(BaseConstantsClass):
            foo = 4, attrs(data=[1, 2, 3])
        
        assert_equals([1, 2, 3], OptionalData.data_for(OptionalData.foo))

    def test_can_add_custom_data_with_arbitrary_attribute_names(self):
        data_as_list = attrs(data=[42, 21])
        assert_equals([42, 21], data_as_list.data)

        kw_only = attrs(answer=42, question=21)
        assert_equals(
            {'answer': 42, 'question': 21},
            kw_only.data
        )

        data_as_dict = attrs(data={'answer': 42, 'question': 21})
        assert_equals(
            {'answer': 42, 'question': 21},
            data_as_dict.data
        )

