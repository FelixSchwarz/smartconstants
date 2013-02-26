# -*- coding: UTF-8 -*-

from pythonic_testcase import *

from smart_constants import attrs, BaseConstantsClass


class DummyConstants(BaseConstantsClass):
    foo = "bar"
    bar = "quux"
    
    _fnord = "fnord"
    
    def fnord(self):
        return None

class TestBaseConstantsClass(PythonicTestCase):
    
    def test_private_namen_werden_ignoriert(self):
        assert_not_contains("_fnord", DummyConstants.constants())
    
    def test_funktionen_werden_ignoriert(self):
        assert_not_contains("fnord", DummyConstants.constants())
    
    def test_kann_namen_aller_definierten_konstanten_abrufen(self):
        assert_equals(("foo", "bar"), DummyConstants.constants())
    
    def test_kann_werte_aller_definierten_konstanten_abrufen(self):
        assert_equals(("bar", "quux"), DummyConstants.values())
    
    def test_kann_konstantenname_fuer_gegebenen_wert_ermitteln(self):
        assert_equals("bar", DummyConstants.constant_for("quux"))


class CodesWithAttributes(BaseConstantsClass):
    foo = 4, attrs(label="Foo")
    bar = 5, attrs(label="Bar")
    qux = 2, attrs(label="Quux")


class CodesWithHiddenAttributes(BaseConstantsClass):
    foo = 4, attrs(label="Foo", visible=False)
    bar = 5, attrs(label="Bar", visible=True)

class TestMethodAutoGenerationForBaseConstants(PythonicTestCase):
    
    def test_kann_values_auch_mit_erweiterten_attributen_ermitteln(self):
        assert_equals((4, 5, 2), CodesWithAttributes.values())
    
    def test_kann_wert_fuer_konstante_einfach_verwenden(self):
        assert_equals(4, CodesWithAttributes.foo)
    
    def test_kann_constants_auch_mit_erweiterten_attributen_ermitteln(self):
        assert_equals(("foo", "bar", "qux"), CodesWithAttributes.constants())
    
    def test_kann_optionen_fuer_select_automatisch_generieren(self):
        assert_equals(((4, "Foo"), (5, "Bar"), (2, "Quux")), 
                      CodesWithAttributes.options())
    
    def test_ausgeblendete_optionen_tauchen_nicht_im_select_auf(self):
        assert_equals(((5, "Bar"),), CodesWithHiddenAttributes.options())
    
    def test_optionen_fuer_select_enthaelt_auch_bisherigen_wert_selbst_wenn_nicht_sichtbar(self):
        """Wenn ein Wert nicht mehr im Select-Feld sichtbar ist, würde automatisch
        ein anderer Wert im Select-Feld ausgewählt werden. Dadurch würde beim 
        Speichern des Datensatzes automatisch der Wert geändert, was ggf. nicht
        gewollt ist."""
        assert_equals(((5, "Bar"),), CodesWithHiddenAttributes.options())
        
        options = CodesWithHiddenAttributes.options(current_value=CodesWithHiddenAttributes.foo)
        assert_equals(((4, "Foo"), (5, "Bar")), options)
    
    def test_kann_label_fuer_wert_erhalten(self):
        assert_equals("Foo", CodesWithAttributes.label_for(CodesWithAttributes.foo))
        assert_equals("Quux", CodesWithAttributes.label_for(CodesWithAttributes.qux))
    
    def test_bei_einfachen_konstanten_wird_wert_als_label_verwendet(self):
        assert_equals("quux", DummyConstants.label_for(DummyConstants.bar))


class TestConstantWithEmptyValue(PythonicTestCase):
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

