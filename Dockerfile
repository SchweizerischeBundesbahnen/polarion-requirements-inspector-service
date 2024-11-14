FROM python:3.12.7-slim@sha256:032c52613401895aa3d418a4c563d2d05f993bc3ecc065c8f4e2280978acd249

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
