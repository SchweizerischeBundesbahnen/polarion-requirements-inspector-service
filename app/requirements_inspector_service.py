"""Start and run Polarion Requirements Inspector Service with args"""

import argparse
import importlib
import logging
import os
import sys

from app.constants import POLARION_REQUIREMENTS_INSPECTOR_SERVICE_VERSION_HEADER
from app.requirements_inspector_controller import start_server


def main(port: int, request_size_limit: int, log_level: str) -> None:
    logging.getLogger().setLevel(logging.INFO)
    logging.info("Requirements Inspector Service running on port: %d", port)
    logging.getLogger().setLevel(log_level.upper())

    polarion_requirements_inspector_version = importlib.metadata.version("python-requirements-inspector")
    polarion_requirements_inspector_service_version = os.environ.get(POLARION_REQUIREMENTS_INSPECTOR_SERVICE_VERSION_HEADER.upper())

    if not polarion_requirements_inspector_service_version:
        sys.exit("Service version unknown")

    start_server(port, polarion_requirements_inspector_version, polarion_requirements_inspector_service_version, request_size_limit)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", default=9081, type=int, required=False, help="Service port number")
    parser.add_argument(
        "--request-size-limit",
        default=1 << 24,  # Default 2^24 bytes = 16MB
        type=int,
        required=False,
        help="Maximum size of request for endpoint /inspect/workitems in bytes",
    )
    parser.add_argument("--log-level", default="WARNING", type=str, required=False, help="Service log level")
    args = parser.parse_args()
    main(args.port, args.request_size_limit, args.log_level)
