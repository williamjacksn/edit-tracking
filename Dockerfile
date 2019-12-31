FROM python:3.8.1-alpine3.10

COPY requirements.txt /edit-tracking/requirements.txt

RUN /sbin/apk add --no-cache --virtual .deps gcc musl-dev postgresql-dev \
 && /sbin/apk add --no-cache libpq \
 && /usr/local/bin/pip install --no-cache-dir --requirement /edit-tracking/requirements.txt \
 && /sbin/apk del --no-cache .deps

ENV APP_VERSION="2019.2" \
    PYTHONUNBUFFERED="1" \
    TZ="America/Chicago"

ENTRYPOINT ["/usr/local/bin/python"]
CMD ["/edit-tracking/run.py"]

LABEL org.opencontainers.image.authors="William Jackson <william@subtlecoolness.com>" \
      org.opencontainers.image.source="https://github.com/williamjacksn/edit-tracking" \
      org.opencontainers.image.title="Edit Tracking" \
      org.opencontainers.image.version="${APP_VERSION}"

COPY . /edit-tracking
