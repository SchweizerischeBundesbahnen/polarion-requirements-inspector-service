import logging

from app.requirements_inspector_service import main


def test_sys_exit():
    logging.disable(logging.CRITICAL)
    try:
        main(0, 0)
        raise AssertionError()
    except SystemExit:
        pass
