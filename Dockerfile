FROM python:3.12.7-slim@sha256:2a6386ad2db20e7f55073f69a98d6da2cf9f168e05e7487d2670baeb9b7601c5

LABEL maintainer="SBB Polarion Team <polarion-opensource@sbb.ch>"
ARG APP_IMAGE_VERSION=0.0.0-dev

ENV WORKING_DIR=/opt/polarion_requirements_inspector
ENV POLARION_REQUIREMENTS_INSPECTOR_SERVICE_VERSION=$APP_IMAGE_VERSION

WORKDIR ${WORKING_DIR}

COPY requirements.txt ${WORKING_DIR}/requirements.txt
COPY ./app/ ${WORKING_DIR}/app/
COPY ./poetry.lock ${WORKING_DIR}
COPY ./pyproject.toml ${WORKING_DIR}

RUN pip install --no-cache-dir -r ${WORKING_DIR}/requirements.txt && poetry install

ENTRYPOINT [ "poetry", "run", "python", "-m", "app.requirements_inspector_service" ]
