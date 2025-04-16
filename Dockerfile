FROM python:3.12.9-alpine3.21@sha256:28b8a72c4e0704dd2048b79830e692e94ac2d43d30c914d54def6abf74448a4e
LABEL maintainer="SBB Polarion Team <polarion-opensource@sbb.ch>"

ARG APP_IMAGE_VERSION=0.0.0-dev

# hadolint ignore=DL3018
RUN apk add --no-cache \
    gcc \
    g++ \
    musl-dev \
    python3-dev \
    libffi-dev \
    cmake \
    make \
    cython

ENV WORKING_DIR=/opt/polarion_requirements_inspector
ENV POLARION_REQUIREMENTS_INSPECTOR_SERVICE_VERSION=$APP_IMAGE_VERSION

WORKDIR ${WORKING_DIR}

COPY requirements.txt ${WORKING_DIR}/requirements.txt
COPY README.md ${WORKING_DIR}/README.md
COPY ./app/ ${WORKING_DIR}/app/
COPY ./poetry.lock ${WORKING_DIR}
COPY ./pyproject.toml ${WORKING_DIR}

RUN pip install --no-cache-dir -r ${WORKING_DIR}/requirements.txt && poetry install

ENTRYPOINT [ "poetry", "run", "python", "-m", "app.requirements_inspector_service" ]
