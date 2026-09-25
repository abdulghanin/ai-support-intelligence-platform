import unittest

from support_intelligence.app import get_app_name


class TestApp(unittest.TestCase):
    def test_get_app_name(self) -> None:
        self.assertEqual(
            get_app_name(),
            "AI Support Intelligence Platform",
        )
