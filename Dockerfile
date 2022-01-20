FROM python:3.10.2-alpine3.15

RUN /sbin/apk add --no-cache libpq

COPY requirements.txt /edit-tracking/requirements.txt

RUN /usr/local/bin/pip install --no-cache-dir --requirement /edit-tracking/requirements.txt

ENV APP_VERSION="2021.1" \
    PYTHONUNBUFFERED="1" \
    TZ="America/Chicago"

ENTRYPOINT ["/usr/local/bin/python"]
CMD ["/edit-tracking/run.py"]
HEALTHCHECK CMD ["/usr/bin/wget", "--spider", "--quiet", "http://localhost:8080/health-check"]

LABEL org.opencontainers.image.authors="William Jackson <william@subtlecoolness.com>" \
      org.opencontainers.image.source="https://github.com/williamjacksn/edit-tracking" \
      org.opencontainers.image.title="Edit Tracking" \
      org.opencontainers.image.version="${APP_VERSION}"

COPY . /edit-tracking
