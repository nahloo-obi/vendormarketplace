# FROM python:3.9-alpine3.13
# LABEL maintainer="nalu.com"

# ENV PYTHONBUFFERED 1

# COPY ./requirements.txt /requirements.txt
# COPY . /app
# COPY ./scripts /scripts

# WORKDIR /app
# EXPOSE 8000

# # Install dependencies
# RUN python -m venv /py && \
#     /py/bin/pip install --upgrade pip && \
#     apk add --update --no-cache \
#         postgresql-client \
#         gdal-bin \
#         libgdal-dev \
#         nginx && \
#     apk add --update --no-cache --virtual .tmp-deps \
#         build-base postgresql-dev musl-dev linux-headers && \
#     /py/bin/pip install -r requirements.txt && \
#     apk del .tmp-deps && \
#     adduser --disabled-password --no-create-home app && \
#     mkdir -p /app/staticfiles /app/media && \
#     chown -R app:app /app/staticfiles /app/media && \
#     chmod -R 755 /app/staticfiles /app/media && \
#     chmod -R +x /scripts

# # Set environment variables
# ENV PATH="/scripts:/py/bin:$PATH"

# # Switch to non-root user
# USER app

# # Default command
# CMD ["run.sh"]


# Base image
# FROM python:3.9-alpine3.13
# LABEL maintainer="nalu.com"

# # Set environment variables
# ENV PYTHONBUFFERED=1 \
#     PATH="/scripts:/py/bin:$PATH"

# # Copy files
# COPY ./requirements.txt /requirements.txt
# COPY . /app
# COPY ./scripts /scripts

# # Working directory
# WORKDIR /app

# # Expose application port
# EXPOSE 8000

# # Install dependencies
# RUN python -m venv /py && \
#     /py/bin/pip install --upgrade pip && \
#     apk add --update --no-cache \
#         postgresql-client \
#         gdal-bin \
#         libgdal-dev \
#         nginx && \
#     apk add --update --no-cache --virtual .tmp-deps \
#         build-base postgresql-dev musl-dev linux-headers && \
#     /py/bin/pip install -r requirements.txt && \
#     apk del .tmp-deps && \
#     adduser --disabled-password --no-create-home app && \
#     mkdir -p /app/staticfiles /app/media && \
#     chown -R app:app /app/staticfiles /app/media && \
#     chmod -R 755 /app/staticfiles /app/media && \
#     chmod -R +x /scripts

# # Switch to non-root user
# USER app

# # Default command
# CMD ["run.sh"]

FROM python:3.10-alpine
LABEL maintainer="nalu.com"

ENV PYTHONBUFFERED 1

# Copy the requirements and project files
COPY ./requirements.txt /requirements.txt
COPY . /app
COPY ./scripts /scripts

WORKDIR /app
EXPOSE 8000

# Install dependencies
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache \
        postgresql-client \
        gdal gdal-dev \
        proj proj-dev \
        geos geos-dev && \
    apk add --update --no-cache --virtual .tmp-deps \
        build-base postgresql-dev musl-dev linux-headers && \
    ENV PROJ_DIR=/usr && \
    ENV PATH="/usr/bin:$PATH" && \
    ENV LD_LIBRARY_PATH="/usr/lib:$LD_LIBRARY_PATH" && \
    proj --version && \
    /py/bin/pip install -r requirements.txt && \
    apk del .tmp-deps && \
    adduser --disabled-password --no-create-home app && \
    mkdir -p /app/staticfiles /app/media && \
    chown -R app:app /app/staticfiles /app/media && \
    chmod -R 755 /app/staticfiles /app/media && \
    chmod -R +x /scripts

# Set environment variables
ENV PATH="/scripts:/py/bin:$PATH"

# Switch to non-root user
USER app

# Default command
CMD ["run.sh"]

