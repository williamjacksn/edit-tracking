FROM python:3.8.0-alpine3.10

COPY requirements.txt /edit-tracking/requirements.txt

RUN /usr/local/bin/pip install --no-cache-dir --requirement /edit-tracking/requirements.txt

ENV APP_VERSION="2019.1" \
    PYTHONUNBUFFERED="1" \
    TZ="America/Chicago"

ENTRYPOINT ["/usr/local/bin/python"]
CMD ["/edit-tracking/run.py"]

LABEL org.opencontainers.image.authors="William Jackson <william@subtlecoolness.com>" \
      org.opencontainers.image.source="https://github.com/williamjacksn/edit-tracking/" \
      org.opencontainers.image.title="Edit Tracking" \
      org.opencontainers.image.version="${APP_VERSION}"

COPY . /edit-tracking
