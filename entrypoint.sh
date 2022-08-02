#!/usr/bin/env sh

PARAMS="--config-file ${CONFIG_PATH}"
PARAMS=$PARAMS" --log-level ${LOG_LEVEL}"

if [ -n "${RUN_DATE}" ]; then
    PARAMS=$PARAMS" --run-date ${RUN_DATE}"
fi

if [ -n "${RUN_USER}" ]; then
    PARAMS=$PARAMS" --user ${RUN_USER}"
fi

if [ "${DRY_RUN}" = "Y" ]; then
    PARAMS=$PARAMS" --dry-run"
fi

echo "Starting caldav_recurring_task_scheduler with params : $PARAMS"
python3 /opt/caldav_recurring_task_scheduler/caldav_recurring_task_scheduler/cli.py $PARAMS
