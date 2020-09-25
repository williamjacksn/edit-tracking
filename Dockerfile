FROM python:3.8.6-alpine3.12

RUN /sbin/apk add --no-cache libpq

COPY requirements.txt /edit-tracking/requirements.txt

RUN /sbin/apk add --no-cache --virtual .deps gcc musl-dev postgresql-dev \
 && /usr/local/bin/pip install --no-cache-dir --requirement /edit-tracking/requirements.txt \
 && /sbin/apk del --no-cache .deps

ENV APP_VERSION="2020.5" \
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
