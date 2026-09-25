import os
import unittest
from unittest.mock import patch

from support_intelligence.config import get_app_env


class TestConfig(unittest.TestCase):
    def test_reads_app_env(self) -> None:
        with patch.dict(os.environ, {"APP_ENV": "testing"}):
            self.assertEqual(get_app_env(), "testing")

    def test_uses_default_when_missing(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(get_app_env(), "development")