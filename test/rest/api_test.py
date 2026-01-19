import http.client
import os
import unittest
from urllib.request import urlopen
from urllib.error import HTTPError

import pytest

# Importar el módulo api para que coverage lo registre
from app import api

BASE_URL = "http://localhost:5001"
BASE_URL_MOCK = "http://localhost:9090"
DEFAULT_TIMEOUT = 2  # in secs

@pytest.mark.api
class TestApi(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(BASE_URL, "URL no configurada")
        self.assertTrue(len(BASE_URL) > 8, "URL no configurada")

    def test_api_add(self):
        url = f"{BASE_URL}/calc/add/1/2"
        response = urlopen(url, timeout=DEFAULT_TIMEOUT)
        self.assertEqual(
            response.status, http.client.OK, f"Error en la petición API a {url}"
        )
        self.assertEqual(
            response.read().decode(), "3", "ERROR ADD"
        )

    def test_api_sqrt(self):
        url = f"{BASE_URL_MOCK}/calc/sqrt/64"
        response = urlopen(url, timeout=DEFAULT_TIMEOUT)
        self.assertEqual(
            response.status, http.client.OK, f"Error en la petición API a {url}"
        )
        self.assertEqual(
            response.read().decode(), "8", "ERROR SQRT"
        )

    def test_api_substract(self):
        url = f"{BASE_URL}/calc/substract/10/3"
        response = urlopen(url, timeout=DEFAULT_TIMEOUT)
        self.assertEqual(
            response.status, http.client.OK, f"Error en la petición API a {url}"
        )
        self.assertEqual(
            response.read().decode(), "7", "ERROR SUBSTRACT"
        )

    def test_api_hello(self):
        url = f"{BASE_URL}/"
        response = urlopen(url, timeout=DEFAULT_TIMEOUT)
        self.assertEqual(
            response.status, http.client.OK, f"Error en la petición API a {url}"
        )
        self.assertIn("Hello", response.read().decode(), "ERROR HELLO")

    def test_api_add_invalid_params(self):
        url = f"{BASE_URL}/calc/add/invalid/2"
        try:
            response = urlopen(url, timeout=DEFAULT_TIMEOUT)
            self.fail("Debería lanzar HTTPError con código 400")
        except HTTPError as e:
            self.assertEqual(e.code, http.client.BAD_REQUEST)

    def test_api_substract_invalid_params(self):
        url = f"{BASE_URL}/calc/substract/5/invalid"
        try:
            response = urlopen(url, timeout=DEFAULT_TIMEOUT)
            self.fail("Debería lanzar HTTPError con código 400")
        except HTTPError as e:
            self.assertEqual(e.code, http.client.BAD_REQUEST)

if __name__ == "__main__":  # pragma: no cover
    unittest.main()
