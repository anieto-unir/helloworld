import unittest
import pytest

from app import util
from app.util import convert_to_number


@pytest.mark.unit
class TestUtil(unittest.TestCase):
    def test_convert_to_number_correct_param(self):
        self.assertEqual(4, util.convert_to_number("4"))
        self.assertEqual(0, util.convert_to_number("0"))
        self.assertEqual(0, util.convert_to_number("-0"))
        self.assertEqual(-1, util.convert_to_number("-1"))
        self.assertAlmostEqual(4.0, util.convert_to_number("4.0"), delta=0.0000001)
        self.assertAlmostEqual(0.0, util.convert_to_number("0.0"), delta=0.0000001)
        self.assertAlmostEqual(0.0, util.convert_to_number("-0.0"), delta=0.0000001)
        self.assertAlmostEqual(-1.0, util.convert_to_number("-1.0"), delta=0.0000001)

    def test_convert_to_number_invalid_type(self):
        self.assertRaises(TypeError, util.convert_to_number, "")
        self.assertRaises(TypeError, util.convert_to_number, "3.h")
        self.assertRaises(TypeError, util.convert_to_number, "s")
        self.assertRaises(TypeError, util.convert_to_number, None)
        self.assertRaises(TypeError, util.convert_to_number, object())

    # Tests adicionales para 100% cobertura de branches
    def test_convert_to_number_invalid(self):
        """Cubre el branch de ValueError"""
        with pytest.raises(TypeError):
            convert_to_number("invalid")

    def test_convert_to_number_valid(self):
        """Asegura cobertura de ambos branches: con punto y sin punto"""
        assert convert_to_number("42") == 42  # Branch: sin punto
        assert convert_to_number("3.14") == 3.14  # Branch: con punto

if __name__ == "__main__":  # pragma: no cover
    unittest.main()