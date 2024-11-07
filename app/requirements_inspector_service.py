"""Start and run Polarion Requirements Inspector Service with args"""

import argparse
import importlib
import logging
import os
import sys

from app.constants import POLARION_REQUIREMENTS_INSPECTOR_SERVICE_VERSION_HEADER
from app.requirements_inspector_controller import start_server

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", default=9081, type=int, required=False, help="Service port number")
    parser.add_argument(
        "--content-length-limit",
        default=1 << 24,  # Default 2^24 bytes = 16MB
        type=int,
        required=False,
        help="Maximum size of request for endpoint /inspect/workitems in bytes",
    )
    args = parser.parse_args()

    logging.getLogger().setLevel(logging.INFO)
    logging.info("Requirements Inspector Service running on port: %d", args.port)
    logging.getLogger().setLevel(logging.WARNING)

    polarion_requirements_inspector_version = importlib.metadata.version("python-requirements-inspector")
    polarion_requirements_inspector_service_version = os.environ.get(POLARION_REQUIREMENTS_INSPECTOR_SERVICE_VERSION_HEADER.upper())

    if not polarion_requirements_inspector_service_version:
        sys.exit("Service version unknown")

    start_server(args.port, polarion_requirements_inspector_version, polarion_requirements_inspector_service_version, args.content_length_limit)
