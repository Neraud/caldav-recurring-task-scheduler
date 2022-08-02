import logging
import argparse
from datetime import datetime, date
from config import ConfigManager
from rescheduler import Rescheduler


parser = argparse.ArgumentParser(description='Exports org policies violations')

parser.add_argument('--config-file', nargs='?',
                    help='Path to the configuration file.', required=True)
parser.add_argument('--run-date', nargs='?',
                    help='Run date, defaults to today. Format YYYYMMDD.', required=False)
parser.add_argument('--user', nargs='?',
                    help='Run for a specific user only.', required=False)
parser.add_argument('--log-level', nargs='?',
                    help='Log level : DEBUG, INFO (default), WARNING, ERROR', default='INFO')
parser.add_argument('--dry-run', help='Dry run, do not update any task',
                    action=argparse.BooleanOptionalAction)

args = parser.parse_args()

numeric_log_level = getattr(logging, args.log_level.upper(), None)
if not isinstance(numeric_log_level, int):
    raise ValueError('Invalid log level: %s' % args.log_level)

logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(message)s', level=numeric_log_level)

logger = logging.getLogger(__name__)

if args.run_date:
    run_date = datetime.strptime(args.run_date, "%Y%m%d")
else:
    run_date = date.today()


config = ConfigManager(args.config_file)

scheduler = Rescheduler(config, run_date, args.dry_run)
scheduler.run_for_all()
