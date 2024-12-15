FROM python:3.13.1-slim@sha256:f41a75c9cee9391c09e0139f7b49d4b1fbb119944ec740ecce4040626dc07bed

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
