from django.test import TestCase
import re

from .utils import generate_api_key


class UtilsTestCase(TestCase):

    def test_generate_key_collision(self):
        # Generate 10000 random keys and check for a collision
        iterations = 10000
        result = set()
        for i in range(iterations):
            result.add(generate_api_key())

        self.assertEquals(iterations, len(result))

    def test_generate_key_format(self):
        key_fmt = "^[a-zA-z0-9]{32}$"
        for i in range(10):
            self.assertIsNotNone(re.match(key_fmt, generate_api_key()))
