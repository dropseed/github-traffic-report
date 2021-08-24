FROM python:3

COPY requirements.txt /requirements.txt

RUN pip install -U pip && pip install -r /requirements.txt

COPY github_traffic_report /github_traffic_report

WORKDIR /

RUN echo '#!/bin/sh -ex\npython3 -m github_traffic_report "$@"' > /entrypoint.sh && chmod +x /entrypoint.sh

ENTRYPOINT [ "/entrypoint.sh" ]
