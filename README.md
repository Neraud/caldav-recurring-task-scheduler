# CalDAV Recurring task scheduler

This project is meant as a workaround to use recurring tasks on a CalDAV instance that doesn't support it natively.

## Supported servers

It has been tested on [Nexctloud](https://nextcloud.com/) with the [Tasks](https://apps.nextcloud.com/apps/tasks) application.

But it should work with other CalDAV servers.

## How does it work ?

It is basically a CalDAV client that clones tasks based on categories and schedules.

It is meant to be scheduled to run daily.

For all configured users, it :

* looks for configured schedules
* filters schedules to keep only those applicable today
* look for past tasks matching applicable schedules (date and category)
* look for an existing clone of the past task
* clone those tasks if it's not cloned yet

## Schedules

The application supports different types of schedules.

### Regular schedules

The regular schedules are :

* every x days
* every x weeks
* every x months
* every x years

### Monthday schedules

They support cases like '1st Monday of the month' or 'last Saturday of the month'.

## Behaviour

Tasks are cloned with all their existing attributes.

### Updated attributes

On the clone, the following attributes are updated :

* `uid` and `dtstamp` are deleted and regenerated on save
* `completed`, `status` and `percent_complete` are deleted
* `created` and `last-modified` are set to now
* `dtstart` and `due` are postponed according to the schedule
* `summary` can be optionally updated with a suffix (like ' (CLONED)'), mainly for tests purposes

### Cloning subtasks

By default, if a task has a parent, the clone is still attached to the same parent.

This can be changed by setting `detach_from_parent` to `true` in the config.

### Cloning a task with subtasks

By default, the app recursively clones all subtasks of a matching task.

This can be changed by setting `clone_children` to `false` in the config.

## Running the app

### Configuration

Prepare a configuration file.

A minimal configuration looks like this :

```yaml
config:
  default:
    url: http://localhost:8080/remote.php/dav/
    schedules:
      - category: "monthly"
        type: regular
        unit: months
        value: 1
      - category: "weekly"
        type: regular
        unit: weeks
        value: 1
  users:
  - name: some_username
    password: some_password

```

See [Configurations](docs/Configurations.md) for more details.

### Natively

The application can be installed natively and run using cron for example.

To install the application :

```bash
# Recommended, create a virtualenv
python3 -m venv /path/to/caldav_recurring_task_scheduler
source /path/to/caldav_recurring_task_scheduler/bin/activate
# Install the app
python3 -m pip install .
```

Then run the application :

```bash
python3 -m pip install caldav_recurring_task_scheduler \
    --config-file /path/to/config.yaml
```

The cli supports the following parameters :

| Parameter                   | Default value | Description                               |
| --------------------------- | ------------- | ----------------------------------------- |
| -h                          |               | Print the cli help                        |
| --config-file [CONFIG_FILE] |               | Mandatory, path to the configuration file |
| --run-date [RUN_DATE]       | Today         | Run for a specific date. Format YYYYMMDD  |
| --user [USER]               | (absent)      | Run for a specific user only.             |
| --log-level [LOG_LEVEL]     | INFO          | Log level : DEBUG, INFO, WARNING, ERROR   |
| --dry-run                   | (absent)      | Do not update or create any task          |

### Docker

You can build the docker image :

```bash
docker build . -t caldav_recurring_task_scheduler:latest
```

Then run the container :

```bash
docker run -it \
    -v /tmp/config.yaml:/data/config.yaml \
    caldav_recurring_task_scheduler:latest
```

You might need to add a network to make sure the application can access the CalDAV server.
For example :`--network nextcloud_default`

The image supports environment variables :

| Variable    | Default value     | Description                                     |
| ----------- | ----------------- | ----------------------------------------------- |
| CONFIG_PATH | /data/config.yaml | Path to the configuration file                  |
| RUN_DATE    | Empty             | Run for a specific date. Format YYYYMMDD        |
| RUN_USER    | Empty             | Run for a specific user only.                   |
| LOG_LEVEL   | INFO              | Log level : DEBUG, INFO, WARNING, ERROR         |
| DRY_RUN     | N                 | If set to 'Y', do not update or create any task |

## Limitations

### Based on a schedule, not task status

The logic is based on schedules and doesn't take into account task state.

For example, if you have a weekly task on still ongoing from last week, a new one will be created and the previous one won't be updated.

### Deleted tasks

The logic is based on existing tasks matching a schedule.
If you delete a recurring task (after it has been completed for example), it won't be scheduled again.

### Stateless

The application doesn't remember when it's been run, or which tasks have already been cloned.

If the application is not run for some time, the missing days won't be automatically handled. In this case, you have to manually run the appplication with the `run-date` parameter.

To avoid duplicated clones if the application is run multiple times, it tries check if a recurring task has already been cloned. This check is based on `DTSTART`, `CATEGORIES` and `SUMMARY`.

### Task created the day it starts

When the application runs, it looks by default for tasks that should be started today.
Using it this way means that you can't see tasks in advance.

You can change this behavior by using the `run_date` parameter/environment variable to run the app for a few days in the future.
