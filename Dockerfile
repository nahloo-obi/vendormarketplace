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




# Base image
FROM python:3.9-alpine3.13

# Set working directory
WORKDIR /app

# Install Python virtual environment and basic dependencies
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip

# Update repositories, install dependencies, and debug proj installation
RUN apk add --update --no-cache \
        postgresql-client \
        gdal gdal-dev \
        proj proj-dev \
        geos geos-dev \
        build-base postgresql-dev musl-dev linux-headers && \
    echo "Checking proj installation..." && \
    which proj || echo "proj binary not found!" && \
    proj --version || echo "proj failed to run!" && \
    ls -l /usr/bin && \
    ls -l /usr/local/bin

# Optional: Install proj from source if needed (uncomment if binary is missing)
# RUN apk add --update --no-cache build-base curl && \
#     curl -LO https://download.osgeo.org/proj/proj-9.3.0.tar.gz && \
#     tar -xvzf proj-9.3.0.tar.gz && \
#     cd proj-9.3.0 && \
#     ./configure && \
#     make && make install && \
#     cd .. && rm -rf proj-9.3.0*

# Install Python dependencies
COPY requirements.txt /app/
RUN /py/bin/pip install -r requirements.txt

# Create application user and directories
RUN adduser --disabled-password --no-create-home app && \
    mkdir -p /app/staticfiles /app/media && \
    chown -R app:app /app/staticfiles /app/media && \
    chmod -R 755 /app/staticfiles /app/media

# Copy application files
COPY . /app/

# Change permissions for startup scripts
RUN chmod -R +x /scripts

# Run the application as a non-root user
USER app

# Expose the application port
EXPOSE 8000

# Command to run the application
CMD ["/scripts/start.sh"]

