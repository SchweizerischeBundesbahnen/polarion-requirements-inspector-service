import logging
from unittest import TestCase

from app.requirements_inspector_service import main


class TestService(TestCase):
    @classmethod
    def setUpClass(cls):
        logging.disable(logging.CRITICAL)

    def test_sys_exit(self):
        with self.assertRaises(SystemExit):
            main(0, 0)
