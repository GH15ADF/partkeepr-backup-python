# partkeepr-backup-python
A backup script for [PartKeepr](https://www.partkeepr.org/) inspired by [cabottech/PartKeepr-Backup](https://github.com/cabottech/PartKeepr-Backup) but implemented in Python3. The goal is to provide automated backup for a PartKeepr system that is running in Docker containers (like [mhubig/docker-partkeepr](https://github.com/mhubig/docker-partkeepr/blob/master/crontab)). This script assumes it is running on a Linux host and for remote copies of the backup, can connect to a CIFS file server.

The MariaDB contents are dumped (via mysqldump) and zipped together with the contents of the PartKeepr data and configuration directories.

The configuration and private settings are in the secrets.py file which allows for:

* Configuration of how many local backups to keep
* Configuration of how many remote backups to keep
* Usernames and passwrod for access to the PartKeepr MariaDB and a remote file share
* Paths for various directories

## Setup
1. Add execute to the partkeepr-backup.py script
1. Edit the secrets.py file as needed
1. The log level can be changed in the logging.basicConfig() call. See [Logging Levels](https://docs.python.org/3/library/logging.html#logging-levels) if more details are needed.
1. The script adds the directory where it is executed to the path, so it should run from anywhere.
1. Only standard Python3 libraries are needed.

## Automated
For automated periodic backups, add an entry in the root crontab (e.g., sudo crontab -e). 

for example, the following runs the script every day at 0200 (2:00 AM):
```
0 2 * * * /path/to/the/script/partkeepr-backup-python/partkeepr-backup.py
```
