import unittest
import pytest
from unittest.mock import patch, MagicMock
import http.client

from app.api import add, substract, hello


@pytest.mark.unit
class TestApiUnit(unittest.TestCase):
    """Tests unitarios para las funciones de la API"""

    def test_hello_endpoint(self):
        """Test del endpoint hello"""
        result = hello()
        self.assertIn("Hello", result)
        self.assertIn("Calculator", result)

    @patch('app.api.util.convert_to_number')
    @patch('app.api.CALCULATOR.add')
    def test_add_endpoint_success(self, mock_calc_add, mock_convert):
        """Test del endpoint add con parámetros válidos"""
        mock_convert.side_effect = [5, 3]
        mock_calc_add.return_value = 8
        
        result, status, headers = add("5", "3")
        
        self.assertEqual(result, "8")
        self.assertEqual(status, http.client.OK)
        self.assertEqual(headers["Content-Type"], "text/plain")
        mock_calc_add.assert_called_once_with(5, 3)

    @patch('app.api.util.convert_to_number')
    def test_add_endpoint_type_error(self, mock_convert):
        """Test del endpoint add con error de tipo"""
        mock_convert.side_effect = TypeError("Parameters must be numbers")
        
        result, status, headers = add("invalid", "3")
        
        self.assertIn("Parameters must be numbers", result)
        self.assertEqual(status, http.client.BAD_REQUEST)

    @patch('app.api.util.convert_to_number')
    @patch('app.api.CALCULATOR.substract')
    def test_substract_endpoint_success(self, mock_calc_sub, mock_convert):
        """Test del endpoint substract con parámetros válidos"""
        mock_convert.side_effect = [10, 3]
        mock_calc_sub.return_value = 7
        
        result, status, headers = substract("10", "3")
        
        self.assertEqual(result, "7")
        self.assertEqual(status, http.client.OK)
        self.assertEqual(headers["Content-Type"], "text/plain")
        mock_calc_sub.assert_called_once_with(10, 3)

    @patch('app.api.util.convert_to_number')
    def test_substract_endpoint_type_error(self, mock_convert):
        """Test del endpoint substract con error de tipo"""
        mock_convert.side_effect = TypeError("Operator cannot be converted to number")
        
        result, status, headers = substract("10", "invalid")
        
        self.assertIn("cannot be converted", result)
        self.assertEqual(status, http.client.BAD_REQUEST)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
