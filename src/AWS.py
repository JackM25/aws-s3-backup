import boto3
import os
import sys
import threading
from botocore.exceptions import ClientError


class AWSProgressPercentage(object):

    def __init__(self, filename, logger):
        self._filename = filename
        self._logger = logger
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            self._logger.info(
                "Uploading %s  %s / %s  (%.2f%%)" % (
                    self._filename, self._seen_so_far, self._size,
                    percentage))


class AWS:
    """Logic for communicating with AWS via API"""

    def __init__(self, access_key, secret_key, bucket, storage_class, logger):
        self._logger = logger
        self._s3_client = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )
        self._bucket = bucket
        self._storage_class = storage_class
        self._logger.debug("AWS interface initialised")

    def upload_archive(self, archive):
        self._logger.info("Starting upload of archive %s...",
                          archive.get_name())
        try:
            response = self._s3_client.upload_file(archive.location, self._bucket, archive.get_file_name(),
                                                   ExtraArgs={
                                                       'StorageClass': self._storage_class,
                                                       'Metadata': {
                                                           'client': 'aws-s3-backup',
                                                           'key': archive.key,
                                                           'version': archive.version,
                                                           'date': archive.date.isoformat(),
                                                           'size': str(archive.size),
                                                           'raw_size': str(archive.raw_size)
                                                       }},
                                                   Callback=AWSProgressPercentage(archive.location, self._logger))
        except ClientError as e:
            self._logger.error(e)
            return False

        archive.update_location(self._get_arn_for_archive(archive))
        self._logger.info("Archive uploaded successfully")
        return True

    def _get_arn_for_archive(self, archive):
        return 'arn:aws:s3:::' + self._bucket + '/' + archive.get_file_name()
