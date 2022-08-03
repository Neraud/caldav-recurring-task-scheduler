# Configurations

This app is configured using a yaml file.

It has a `default` and a `users` sections.

All values under `default` can also be set under a specific user.

```yaml
config:
  default:
    url: http://localhost:8080/remote.php/dav/
    schedules: []
  users: []
```

## Default

```yaml
config:
  default:
    url: http://localhost:8080/remote.php/dav/
    ssl_verify_cert: True
    ssl_cert: None
    clone_children: True
    detach_from_parent: False
    clone_summary_suffix: ""
    timezone: "UTC"
    schedules: []
```

* `config.default.url` : the URL of your default CalDav server
* `config.default.ssl_verify_cert` and `config.default.ssl_cert`: to configure SSL if required
* `config.default.clone_children` : to recursively clone subtasks of a matching task
* `config.default.detach_from_parent` : to detach a matching task from its parent
* `config.default.clone_summary_suffix` : to add a suffix to the summary of cloned tasks (for example ` (CLONED)`). Mainly used to debug purposes
* `config.default.timezone` : the timezone used by the tasks
* `config.default.schedules` : a list of default schedules

### Note about timezone

The Nextcloud Tasks application doesn't support timezone. But the Python CalDAV client does.

If we apply a filter using a local timezone, the client will properly convert it to UTC.
For example, if we use 4pm UTC+2, the client will send 2pm UTC, and Nextcloud will think it means 2pm UTC+2.

The timezone must be forced to `UTC` to avoid issues.

## Schedules

A schedule always has :

* `category` : the category to match on a task
* `type` : the type of schedule

Depending on the `type`, they have different attributes.

### Regular schedules

`regular` schedules have:

* `unit`: `days`, `weeks`, `months` or `years`
* `value` : the number of `unit` between 2 occurrences

```yaml
- category: "3-days"
  type: regular
  unit: days
  offset: 3
- category: "weekly"
  type: regular
  unit: weeks
  offset: 1
- category: "monthly"
  type: regular
  unit: months
  offset: 1
```

### Monthday schedules

`monthday` schedules have:

* `day` : the day of the week (`MO`, `TU`, `WE`, `TH`, `FR`, `SA`, `SU`)
* `n` : the `n`th occurence. Can be positive (1st, 2nd, ...), or negative (last, ...). 

```yaml
- category: "first-monday"
  type: monthday
  day: "MO"
  n: 1
- category: "second-tuesday"
  type: monthday
  day: "TU"
  n: 2
- category: "last-monday"
  type: monthday
  day: "MO"
  n: -1
```

## Users

Each user has its block of configuration.

```yaml
config:
  users:
  - name: user_name
    password: password
    (any property from default)
```

A user must have :

* `username`
* `password`

It can also define any property used in the [default] section.
