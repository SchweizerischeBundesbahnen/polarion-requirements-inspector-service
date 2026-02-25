import logging
import os

from app.constants import POLARION_REQUIREMENTS_INSPECTOR_SERVICE_VERSION_HEADER
from app.requirements_inspector_service import main
from unittest.mock import patch
from app.requirements_inspector_service import parse_args


def test_sys_exit():
    logging.disable(logging.CRITICAL)
    try:
        main(0, 0, "INFO")
        raise AssertionError("System did not exit")
    except SystemExit:
        pass

def test_main_with_args():
    env_key = POLARION_REQUIREMENTS_INSPECTOR_SERVICE_VERSION_HEADER.upper()
    with patch.dict(os.environ, {env_key: "1.0.0"}, clear=False):
        try:
            main(-1, 0, "INFO")
            raise AssertionError("System did not exit")
        except SystemExit:
            pass


def test_parse_args_with_defaults():
    with patch('sys.argv', ['prog']):
        port, request_size_limit, log_level = parse_args()
        assert port == 9081
        assert request_size_limit == 16777216  # 2^24
        assert log_level == "WARNING"

def test_parse_args_with_custom_values():
    with patch('sys.argv', ['prog', '--port', '8080', '--request-size-limit', '1000000', '--log-level', 'DEBUG']):
        port, request_size_limit, log_level = parse_args()
        assert port == 8080
        assert request_size_limit == 1000000
        assert log_level == "DEBUG"

def test_parse_args_partial_override():
    with patch('sys.argv', ['prog', '--port', '9090']):
        port, request_size_limit, log_level = parse_args()
        assert port == 9090
        assert request_size_limit == 16777216
        assert log_level == "WARNING"
