# AWS S3 Backup
A Python script for backing up files to a bucket within AWS S3

## How it works
This script makes use of a data file to store all information required for it to run. This is divided into two sections; `properties` which should be edited as required and `state` which stores information on files that have been backed up in previous runs.

Using the list of `backup_locations`, the script first identifies any files and folders that have changed. This is detected by comparing the size to the size of the file/folder when it was last backed up. Once this list of files/folders is calculated, each file/folder is then zipped and the pushed to the specified AWS S3 bucket, using the storage type defined in the `aws` section of the data file. Zip folders in AWS S3 are considered immutable and if a change is detected the whole folder is zipped and backed up again.

## Requirements
* Python 3.8.0 or higher
* Pipenv installed and on the path

## Installation
Download or clone this repository to your local machine:
```
git clone https://github.com/JackM25/aws-s3-backup.git
```
* Optionally, the `/bin` folder of this repository can be added to the `PATH`.

### AWS Configuration
1. Create an S3 bucket
   * Choose a name, region, options and permissions as required. The bucket should then be added to the `properties` in the data file.
2. Create an IAM user
   * It is recommended to create a new user with just the permissions required
   * For the script, the only required permission is `s3:PutObject` on the S3 bucket to be used
   ```
    {
        "Sid": "<SID>",
        "Effect": "Allow",
        "Action": "s3:PutObject",
        "Resource": "arn:aws:s3:::<BUCKET_NAME>/*"
    },
   ```
   * The Access Key and Secret Key for this user should be set in the `aws` section of the data file.

### Local Configuration
1. Copy `/s3-backup.example.json` and place it alongside the files/folders to be backed up. This file should not be placed inside any folder that will be backed up. This file may also be renamed at this point if required.
2. Open your copy of the `/s3-backup.example.json` data file and fill in the following in the `properties` section:
   * `backup_locations`: This is a list of all top level locations that should be backed up. All files and folders immediately below the locations listed here will be backed up as separate zip archives. `path` is the full location to this top level folder. `key` is an identifier for this folder, that will be prepended to the zip file when uploaded to AWS. It is important that this key is unique for each backup location.
   ```
    {
      "key": "<KEY>",
      "path": "<FULL_PATH>"
    }
   ```
   * `aws:access_key`: The AWS access key for the user account to use to upload the files to the S3 bucket.
   * `aws:secret_key`: The AWS secret key for the user account to use to upload the files to the S3 bucket.
   * `aws:bucket`: The name of the AWS bucket to upload the files to.
   * `aws:storage_class`: The AWS S3 storage class to use. This should be one of `STANDARD`, `REDUCED_REDUNDANCY`, `STANDARD_IA`, `ONEZONE_IA`, `INTELLIGENT_TIERING`, `GLACIER` or `DEEP_ARCHIVE`.

## Usage
To run the script call
```
pipenv run main.py -f <path_to_data_file>
```
where `pipenv run main.py` can be replaced with `aws_s3_backup` if the `/bin` folder has been added to your path.

The option flag `--dry-run` can be added to the above command to show files that will be backed up without actually performing the backup.
```
pipenv run main.py -f <path_to_data_file> --dry-run
```

## Licence
Licensed under the MIT licence. I accept no responsibility for any damage or loss to data when using this script. Ensure you understand what this script does before running it and follow best practices when using it with important data, such as testing it thoroughly before use.