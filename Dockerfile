FROM python:3.13.0-alpine3.20

ENV CONFIG_PATH=/data/config.yaml
ENV LOG_LEVEL=INFO
ENV RUN_DATE=""
ENV RUN_USER ""
ENV DRY_RUN="N"

RUN adduser app -D

ADD --chown=app:app . /opt/caldav_recurring_task_scheduler
RUN chmod +x /opt/caldav_recurring_task_scheduler/entrypoint.sh

USER app

RUN python3 -m pip install /opt/caldav_recurring_task_scheduler

ENTRYPOINT [ "/opt/caldav_recurring_task_scheduler/entrypoint.sh" ]
