FROM python:3.12.9-slim@sha256:a866731a6b71c4a194a845d86e06568725e430ed21821d0c52e4efb385cf6c6f

LABEL maintainer="SBB Polarion Team <polarion-opensource@sbb.ch>"
ARG APP_IMAGE_VERSION=0.0.0-dev

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
