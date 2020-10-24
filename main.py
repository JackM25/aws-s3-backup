import argparse
import logging
from src.Data import Data
from src.FileSystem import FileSystem
from src.SyncManager import SyncManager
from src.AWS import AWS


def main(data_file_location, dry_run):
    logger = create_logger()
    logger.info('Starting AWS S3 Backup...')
    file_system = FileSystem(logger)
    data = Data(data_file_location, logger)
    aws = AWS(data.aws_access_key(), data.aws_secret_key(),
              data.aws_bucket(), data.aws_storage_class(), logger)
    sync_manager = SyncManager(file_system, aws, logger)
    sync_manager.run(data, dry_run)


def create_logger(log_level=logging.DEBUG):
    # Create logger
    logger = logging.getLogger('aws_s3_backup')
    logger.setLevel(log_level)
    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger


if __name__ == '__main__':
    # We are running command line, parse args and call main
    parser = argparse.ArgumentParser(description='AWS S3 backup process')
    parser.add_argument('-f', action='store', required=True,
                        help='Location of the data file', dest='data_file_location')
    parser.add_argument('--dry-run', action='store_true',
                        help='List changes without syncing to AWS', dest='dry_run')
    input_args = parser.parse_args()
    main(input_args.data_file_location, input_args.dry_run)
